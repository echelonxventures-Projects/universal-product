"""Unit tests for engine.graph.architecture.algorithms.

Every test proves a *behaviour* the module's docstrings legislate: canonical ordering
(the determinism gate), stack-safe traversal, total SCC partitioning, DAG-ness of the
condensation, and fail-closed rejection of cyclic input where a DAG is required.
"""

from __future__ import annotations

import pytest

from engine.graph.architecture.algorithms import (
    condensation,
    cyclic_components,
    longest_paths,
    normalise_adjacency,
    reconstruct_path,
    strongly_connected_components,
    topological_order,
)

# --- normalise_adjacency ---------------------------------------------------------


def test_normalise_adjacency_keys_every_node_and_sorts_successors():
    adj = normalise_adjacency(["c", "a", "b"], [("a", "c"), ("a", "b")])
    # every node is a key, in sorted order; isolated nodes map to an empty tuple
    assert list(adj) == ["a", "b", "c"]
    assert adj["a"] == ("b", "c")
    assert adj["b"] == ()
    assert adj["c"] == ()


def test_normalise_adjacency_deduplicates_repeated_edges():
    adj = normalise_adjacency(["a", "b"], [("a", "b"), ("a", "b"), ("a", "b")])
    assert adj["a"] == ("b",)


def test_normalise_adjacency_drops_self_edges():
    # a self-edge is not a dependency between two nodes and must not appear
    adj = normalise_adjacency(["a", "b"], [("a", "a"), ("a", "b")])
    assert adj["a"] == ("b",)


def test_normalise_adjacency_ignores_edges_with_unknown_endpoints():
    adj = normalise_adjacency(["a", "b"], [("a", "ghost"), ("ghost", "b"), ("a", "b")])
    assert adj == {"a": ("b",), "b": ()}


def test_normalise_adjacency_is_deterministic_across_input_orderings():
    forward = normalise_adjacency(["a", "b", "c"], [("a", "b"), ("b", "c")])
    reverse = normalise_adjacency(["c", "b", "a"], [("b", "c"), ("a", "b")])
    assert forward == reverse
    assert list(forward) == list(reverse)


def test_normalise_adjacency_empty_graph():
    assert normalise_adjacency([], []) == {}


# --- strongly_connected_components -----------------------------------------------


def test_scc_partitions_every_node_exactly_once():
    adj = normalise_adjacency(
        ["a", "b", "c", "d"], [("a", "b"), ("b", "a"), ("b", "c"), ("c", "d")]
    )
    comps = strongly_connected_components(adj)
    flattened = [node for comp in comps for node in comp]
    assert sorted(flattened) == ["a", "b", "c", "d"]
    assert len(flattened) == len(set(flattened))  # exactly once


def test_scc_groups_a_mutual_cycle_and_isolates_acyclic_nodes():
    adj = normalise_adjacency(
        ["a", "b", "c", "d"], [("a", "b"), ("b", "a"), ("b", "c"), ("c", "d")]
    )
    assert strongly_connected_components(adj) == (("a", "b"), ("c",), ("d",))


def test_scc_finds_all_components_not_just_one():
    # two disjoint 2-cycles: EPIC-002 find_cycle returns one, this must return both
    adj = normalise_adjacency(
        ["a", "b", "x", "y"], [("a", "b"), ("b", "a"), ("x", "y"), ("y", "x")]
    )
    assert strongly_connected_components(adj) == (("a", "b"), ("x", "y"))


def test_scc_handles_a_three_node_cycle():
    adj = normalise_adjacency(["a", "b", "c"], [("a", "b"), ("b", "c"), ("c", "a")])
    assert strongly_connected_components(adj) == (("a", "b", "c"),)


def test_scc_ordering_is_canonical_and_independent_of_insertion_order():
    edges = [("b", "c"), ("c", "b"), ("a", "b")]
    first = strongly_connected_components(normalise_adjacency(["a", "b", "c"], edges))
    second = strongly_connected_components(
        normalise_adjacency(["c", "b", "a"], list(reversed(edges)))
    )
    assert first == second == (("a",), ("b", "c"))


def test_scc_ignores_successors_absent_from_the_adjacency():
    # a dangling successor is not a node of this graph and must not be traversed
    adj = {"a": ("b", "ghost"), "b": ()}
    assert strongly_connected_components(adj) == (("a",), ("b",))


def test_scc_is_stack_safe_on_a_deep_chain():
    # iterative Tarjan: a chain far deeper than the interpreter recursion limit
    depth = 5000
    nodes = [f"n{i:05d}" for i in range(depth)]
    edges = [(nodes[i], nodes[i + 1]) for i in range(depth - 1)]
    comps = strongly_connected_components(normalise_adjacency(nodes, edges))
    assert len(comps) == depth
    assert all(len(comp) == 1 for comp in comps)


def test_scc_is_stack_safe_on_a_deep_cycle():
    depth = 5000
    nodes = [f"n{i:05d}" for i in range(depth)]
    edges = [(nodes[i], nodes[(i + 1) % depth]) for i in range(depth)]
    comps = strongly_connected_components(normalise_adjacency(nodes, edges))
    assert len(comps) == 1
    assert len(comps[0]) == depth


def test_scc_empty_graph():
    assert strongly_connected_components({}) == ()


# --- cyclic_components -----------------------------------------------------------


def test_cyclic_components_reports_multi_member_cycles_only():
    adj = normalise_adjacency(["a", "b", "c"], [("a", "b"), ("b", "a"), ("b", "c")])
    assert cyclic_components(adj) == (("a", "b"),)


def test_cyclic_components_excludes_healthy_singletons():
    adj = normalise_adjacency(["a", "b"], [("a", "b")])
    assert cyclic_components(adj) == ()


def test_cyclic_components_includes_a_self_loop_singleton():
    # normalise_adjacency strips self-edges, so a self-loop is expressed directly
    adj = {"a": ("a",), "b": ()}
    assert cyclic_components(adj) == (("a",),)


def test_cyclic_components_reports_every_cycle():
    adj = normalise_adjacency(
        ["a", "b", "x", "y", "z"],
        [("a", "b"), ("b", "a"), ("x", "y"), ("y", "x"), ("z", "a")],
    )
    assert cyclic_components(adj) == (("a", "b"), ("x", "y"))


# --- condensation ----------------------------------------------------------------


def test_condensation_collapses_each_cycle_into_one_super_node():
    adj = normalise_adjacency(["a", "b", "c"], [("a", "b"), ("b", "a"), ("b", "c")])
    dag, member_of, members = condensation(adj)
    assert members == {"SCC::a": ("a", "b"), "SCC::c": ("c",)}
    assert member_of == {"a": "SCC::a", "b": "SCC::a", "c": "SCC::c"}
    assert dag == {"SCC::a": ("SCC::c",), "SCC::c": ()}


def test_condensation_result_is_acyclic_even_when_input_is_not():
    adj = normalise_adjacency(["a", "b", "c"], [("a", "b"), ("b", "c"), ("c", "a")])
    dag, _, _ = condensation(adj)
    # a single SCC with no self-edge: topological_order proves DAG-ness
    assert topological_order(dag) == ("SCC::a",)


def test_condensation_drops_intra_component_edges():
    adj = normalise_adjacency(["a", "b"], [("a", "b"), ("b", "a")])
    dag, _, members = condensation(adj)
    assert members == {"SCC::a": ("a", "b")}
    assert dag == {"SCC::a": ()}  # no self-edge


def test_condensation_component_id_cannot_collide_with_a_node_id():
    adj = normalise_adjacency(["a"], [])
    _, member_of, members = condensation(adj)
    assert member_of["a"] == "SCC::a"
    assert "a" not in members  # the component id is namespaced, not the raw node id


def test_condensation_of_a_dag_is_the_dag_itself():
    adj = normalise_adjacency(["a", "b", "c"], [("a", "b"), ("b", "c")])
    dag, _, members = condensation(adj)
    assert members == {"SCC::a": ("a",), "SCC::b": ("b",), "SCC::c": ("c",)}
    assert dag == {"SCC::a": ("SCC::b",), "SCC::b": ("SCC::c",), "SCC::c": ()}


def test_condensation_ignores_dangling_targets():
    dag, member_of, _ = condensation({"a": ("b", "ghost"), "b": ()})
    assert "ghost" not in member_of
    assert dag == {"SCC::a": ("SCC::b",), "SCC::b": ()}


# --- topological_order -----------------------------------------------------------


def test_topological_order_respects_dependencies():
    adj = normalise_adjacency(["a", "b", "c"], [("a", "b"), ("b", "c")])
    assert topological_order(adj) == ("a", "b", "c")


def test_topological_order_breaks_ties_on_smallest_id():
    # b and c are both ready after a; the smaller id must come first
    adj = normalise_adjacency(["a", "b", "c"], [("a", "b"), ("a", "c")])
    assert topological_order(adj) == ("a", "b", "c")


def test_topological_order_is_deterministic_for_independent_nodes():
    adj = normalise_adjacency(["z", "m", "a"], [])
    assert topological_order(adj) == ("a", "m", "z")


def test_topological_order_rejects_a_cycle_fail_closed():
    adj = normalise_adjacency(["a", "b"], [("a", "b"), ("b", "a")])
    with pytest.raises(ValueError, match="not a DAG"):
        topological_order(adj)


def test_topological_order_rejects_a_partial_cycle():
    # 'a' is orderable but the b<->c cycle is not: the whole call must fail closed
    adj = normalise_adjacency(["a", "b", "c"], [("a", "b"), ("b", "c"), ("c", "b")])
    with pytest.raises(ValueError, match="not a DAG"):
        topological_order(adj)


def test_topological_order_ignores_dangling_targets():
    assert topological_order({"a": ("b", "ghost"), "b": ()}) == ("a", "b")


def test_topological_order_empty_graph():
    assert topological_order({}) == ()


def test_topological_order_insert_sorted_keeps_the_ready_set_ordered():
    # a fans out to many nodes released in one step; order must be fully sorted,
    # which exercises the binary insertion on a non-trivial ready list
    targets = [f"n{i:02d}" for i in range(20)]
    adj = normalise_adjacency(["a", *targets], [("a", t) for t in targets])
    assert topological_order(adj) == ("a", *sorted(targets))


# --- longest_paths ---------------------------------------------------------------


def test_longest_paths_counts_nodes_on_the_longest_chain_by_default():
    adj = normalise_adjacency(["a", "b", "c"], [("a", "b"), ("b", "c")])
    dist, nxt = longest_paths(adj)
    assert dist == {"a": 3, "b": 2, "c": 1}
    assert nxt == {"a": "b", "b": "c", "c": None}


def test_longest_paths_selects_the_heavier_branch():
    #      /-> b -> c   (3 nodes)
    #  a --
    #      \-> d        (2 nodes)
    adj = normalise_adjacency(["a", "b", "c", "d"], [("a", "b"), ("b", "c"), ("a", "d")])
    dist, nxt = longest_paths(adj)
    assert dist["a"] == 3
    assert nxt["a"] == "b"


def test_longest_paths_honours_node_weights():
    adj = normalise_adjacency(["a", "b", "d"], [("a", "b"), ("a", "d")])
    # d is heavier than b, so the weighted longest path goes through d
    dist, nxt = longest_paths(adj, weights={"a": 1, "b": 2, "d": 50})
    assert nxt["a"] == "d"
    assert dist["a"] == 51


def test_longest_paths_falls_back_to_weight_one_for_unweighted_nodes():
    adj = normalise_adjacency(["a", "b"], [("a", "b")])
    dist, _ = longest_paths(adj, weights={"a": 10})  # b unweighted -> 1
    assert dist == {"a": 11, "b": 1}


def test_longest_paths_breaks_ties_on_the_smallest_successor_id():
    # b and c yield identical totals; the deterministic choice is the smaller id
    adj = normalise_adjacency(["a", "b", "c"], [("a", "b"), ("a", "c")])
    dist, nxt = longest_paths(adj)
    assert dist["a"] == 2
    assert nxt["a"] == "b"


def test_longest_paths_terminal_node_has_no_successor():
    dist, nxt = longest_paths(normalise_adjacency(["a"], []))
    assert dist == {"a": 1}
    assert nxt == {"a": None}


def test_longest_paths_rejects_a_cycle_fail_closed():
    adj = normalise_adjacency(["a", "b"], [("a", "b"), ("b", "a")])
    with pytest.raises(ValueError, match="not a DAG"):
        longest_paths(adj)


def test_longest_paths_ignores_dangling_successors():
    dist, nxt = longest_paths({"a": ("b", "ghost"), "b": ()})
    assert dist == {"a": 2, "b": 1}
    assert nxt["a"] == "b"


def test_longest_paths_is_deterministic_across_repeated_runs():
    adj = normalise_adjacency(
        ["a", "b", "c", "d"], [("a", "b"), ("a", "c"), ("b", "d"), ("c", "d")]
    )
    assert longest_paths(adj) == longest_paths(adj)


# --- reconstruct_path ------------------------------------------------------------


def test_reconstruct_path_rebuilds_the_longest_chain():
    adj = normalise_adjacency(["a", "b", "c"], [("a", "b"), ("b", "c")])
    _, nxt = longest_paths(adj)
    assert reconstruct_path(nxt, "a") == ("a", "b", "c")


def test_reconstruct_path_of_a_terminal_node_is_the_node_itself():
    assert reconstruct_path({"a": None}, "a") == ("a",)


def test_reconstruct_path_guards_against_repetition():
    # defensive: a malformed nxt map must terminate rather than loop forever
    assert reconstruct_path({"a": "b", "b": "a"}, "a") == ("a", "b")


def test_reconstruct_path_from_an_unknown_start_yields_just_that_node():
    assert reconstruct_path({}, "ghost") == ("ghost",)


def test_condensation_ignores_an_adjacency_source_no_component_holds(monkeypatch) -> None:
    """THE CONDENSATION IS OVER THE COMPONENTS IT COMPUTED, not over every key the adjacency
    carries — and today those are the same set, which is why the guard has never fired.

    ``strongly_connected_components`` is computed from the same adjacency, so every source
    has a component. The guard is what stands between that invariant and a ``KeyError``
    inside a function whose whole job is to summarise a graph: the day the component set is
    computed some other way — restricted to one layer, or supplied by a caller — a source
    outside it is skipped rather than crashing the summary.
    """

    adjacency = {"a": ("b",), "b": ()}
    dag, member_of, members = condensation(adjacency)
    assert set(members) == {"SCC::a", "SCC::b"}
    assert dag["SCC::a"] == ("SCC::b",)

    monkeypatch.setattr(
        f"{condensation.__module__}.strongly_connected_components",
        lambda _adjacency: (("b",),),
    )
    narrowed_dag, narrowed_member_of, narrowed_members = condensation(adjacency)

    assert set(narrowed_members) == {"SCC::b"}
    assert "a" not in narrowed_member_of
    assert narrowed_dag == {"SCC::b": set()} or narrowed_dag == {"SCC::b": ()}
