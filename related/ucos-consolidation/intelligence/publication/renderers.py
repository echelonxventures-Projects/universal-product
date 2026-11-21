"""Renderers — the open set of output syntaxes for a composed publication.

A renderer turns a :class:`~intelligence.publication.model.ComposedDocument` into a
byte string. Five ship by default (markdown, latex, html, plaintext, json) and
:func:`register_renderer` adds more at runtime, so the *output syntax* space is as
open as the format space.

Every renderer obeys three rules:
  1. **Attribution is mandatory.** Each rendered fragment is followed by the canonical
     reference and the first eight hex of the source content hash, so any reader (or
     auditor) can trace a sentence back to the canonical record that owns it.
  2. **Structural text only.** The renderer contributes headings, separators and the
     generated banner. It never contributes substantive prose.
  3. **Deterministic.** No wall-clock, no locale, no randomness.
"""

from __future__ import annotations

import html as html_lib
from collections.abc import Callable, Iterable

from intelligence.kernel.canonical import canonical_json
from intelligence.kernel.errors import KernelError
from intelligence.kernel.knowledge import ResolvedContent
from intelligence.publication import AUTHORITY, GENERATED_BANNER, PROGRAMME
from intelligence.publication.formats import FormatDescriptor
from intelligence.publication.model import ComposedBlock, ComposedDocument

Renderer = Callable[[ComposedDocument, FormatDescriptor], str]

_DIGEST_PREFIX = 8


def _attribution(resolved: ResolvedContent) -> str:
    return f"[{resolved.ref} · sha256:{resolved.source_content_sha256[:_DIGEST_PREFIX]}]"


def _items(resolved: ResolvedContent) -> list[str]:
    if resolved.value_kind == "list":
        return [line for line in resolved.text.split("\n") if line.strip()]
    return [resolved.text]


def _metadata(document: ComposedDocument) -> list[tuple[str, str]]:
    return [
        ("Publication id", document.publication_id),
        ("Format", f"{document.format_label} ({document.format_id})"),
        ("Genre", document.genre),
        ("Scope", document.area_label),
        ("Programme", PROGRAMME),
        ("Authority", AUTHORITY),
        ("Title source", document.title_ref),
        ("Resolved blocks", str(document.resolved_total())),
        ("Distinct canonical sources", str(len(document.provenance_index()))),
        ("Citations", str(len(document.citations))),
    ]


# ---------------------------------------------------------------------------
# markdown
# ---------------------------------------------------------------------------


def render_markdown(document: ComposedDocument, descriptor: FormatDescriptor) -> str:
    out: list[str] = [f"<!-- {GENERATED_BANNER} -->", ""]
    out.append(f"# {document.format_label}: {document.title}".rstrip(": "))
    out.append("")
    out.append("| Field | Value |")
    out.append("|-------|-------|")
    for key, value in _metadata(document):
        out.append(f"| {key} | {value} |")
    if descriptor.notes:
        out.extend(["", f"> **Note.** {descriptor.notes}"])
    for block in document.blocks:
        if block.section_key == "title-block":
            continue
        if block.structural:
            out.extend(_markdown_structural(document, block))
            continue
        if block.is_empty:
            continue
        out.extend(["", f"## {block.heading}", ""])
        for resolved in block.resolved:
            for item in _items(resolved):
                out.append(f"- {item} {_attribution(resolved)}")
    out.append("")
    return "\n".join(out)


def _markdown_structural(document: ComposedDocument, block: ComposedBlock) -> list[str]:
    if block.section_key == "references":
        lines = ["", f"## {block.heading}", ""]
        if not document.citations:
            lines.append("_no citations_")
            return lines
        lines.append("| # | Canonical reference | Locator | Authority | Research record |")
        lines.append("|---|---------------------|---------|-----------|-----------------|")
        for index, citation in enumerate(document.citations, start=1):
            lines.append(
                f"| {index} | `{citation.ref}` | `{citation.source_locator}` | "
                f"{citation.source_authority} | {citation.research_record_id or '—'} |"
            )
        return lines
    if block.section_key == "provenance":
        lines = ["", f"## {block.heading}", ""]
        lines.append(
            "Every block above is a resolved reference. This publication stores no copy "
            "of canonical content; regenerating it after a canonical change reproduces "
            "the change exactly."
        )
        lines.extend(
            [
                "",
                "| Canonical reference | Locator | Source content hash |",
                "|---------------------|---------|---------------------|",
            ]
        )
        for entry in document.provenance_index():
            lines.append(
                f"| `{entry['ref']}` | `{entry['source_locator']}` | "
                f"`{entry['source_content_sha256']}` |"
            )
        if document.unresolved:
            lines.extend(["", "### Unresolved references", ""])
            for item in document.unresolved:
                lines.append(f"- `{item.get('ref')}` — {item.get('reason')}")
        return lines
    return []


# ---------------------------------------------------------------------------
# latex
# ---------------------------------------------------------------------------

_LATEX_ESCAPES = (
    ("\\", r"\textbackslash{}"),
    ("&", r"\&"),
    ("%", r"\%"),
    ("$", r"\$"),
    ("#", r"\#"),
    ("_", r"\_"),
    ("{", r"\{"),
    ("}", r"\}"),
    ("~", r"\textasciitilde{}"),
    ("^", r"\textasciicircum{}"),
)


def _latex_escape(text: str) -> str:
    out = text
    for needle, replacement in _LATEX_ESCAPES:
        out = out.replace(needle, replacement)
    return out


def render_latex(document: ComposedDocument, descriptor: FormatDescriptor) -> str:
    out = [
        f"% {GENERATED_BANNER}",
        r"\documentclass[11pt]{article}",
        r"\usepackage[T1]{fontenc}",
        r"\usepackage{hyperref}",
        rf"\title{{{_latex_escape(document.title)}}}",
        rf"\author{{{_latex_escape(PROGRAMME)}}}",
        r"\date{}",
        r"\begin{document}",
        r"\maketitle",
    ]
    if descriptor.notes:
        out.append(rf"\begin{{quote}}{_latex_escape(descriptor.notes)}\end{{quote}}")
    for block in document.blocks:
        if block.section_key == "title-block":
            continue
        if block.structural:
            out.extend(_latex_structural(document, block))
            continue
        if block.is_empty:
            continue
        out.append(rf"\section*{{{_latex_escape(block.heading)}}}")
        out.append(r"\begin{itemize}")
        for resolved in block.resolved:
            for item in _items(resolved):
                out.append(
                    rf"  \item {_latex_escape(item)} "
                    rf"\texttt{{{_latex_escape(_attribution(resolved))}}}"
                )
        out.append(r"\end{itemize}")
    out.append(r"\end{document}")
    out.append("")
    return "\n".join(out)


def _latex_structural(document: ComposedDocument, block: ComposedBlock) -> list[str]:
    if block.section_key not in {"references", "provenance"}:
        return []
    rows: Iterable[str]
    if block.section_key == "references":
        rows = (
            rf"  \item \texttt{{{_latex_escape(c.ref)}}} — "
            rf"\texttt{{{_latex_escape(c.source_locator)}}}"
            for c in document.citations
        )
    else:
        rows = (
            rf"  \item \texttt{{{_latex_escape(e['ref'])}}} — "
            rf"\texttt{{{_latex_escape(e['source_content_sha256'])}}}"
            for e in document.provenance_index()
        )
    return [
        rf"\section*{{{_latex_escape(block.heading)}}}",
        r"\begin{itemize}",
        *rows,
        r"\end{itemize}",
    ]


# ---------------------------------------------------------------------------
# html
# ---------------------------------------------------------------------------


def render_html(document: ComposedDocument, descriptor: FormatDescriptor) -> str:
    esc = html_lib.escape
    out = [
        "<!DOCTYPE html>",
        '<html lang="en">',
        "<head>",
        '<meta charset="utf-8">',
        f"<title>{esc(document.title)}</title>",
        f"<!-- {esc(GENERATED_BANNER)} -->",
        "</head>",
        "<body>",
        f"<h1>{esc(document.format_label)}: {esc(document.title)}</h1>",
        "<table><tbody>",
    ]
    for key, value in _metadata(document):
        out.append(f'<tr><th scope="row">{esc(key)}</th><td>{esc(value)}</td></tr>')
    out.append("</tbody></table>")
    if descriptor.notes:
        out.append(f"<blockquote>{esc(descriptor.notes)}</blockquote>")
    for block in document.blocks:
        if block.section_key == "title-block":
            continue
        if block.structural:
            out.extend(_html_structural(document, block))
            continue
        if block.is_empty:
            continue
        out.append(f"<section><h2>{esc(block.heading)}</h2><ul>")
        for resolved in block.resolved:
            for item in _items(resolved):
                out.append(f"<li>{esc(item)} <code>{esc(_attribution(resolved))}</code></li>")
        out.append("</ul></section>")
    out.extend(["</body>", "</html>", ""])
    return "\n".join(out)


def _html_structural(document: ComposedDocument, block: ComposedBlock) -> list[str]:
    esc = html_lib.escape
    if block.section_key == "references":
        rows = [
            f"<li><code>{esc(c.ref)}</code> — <code>{esc(c.source_locator)}</code></li>"
            for c in document.citations
        ]
    elif block.section_key == "provenance":
        rows = [
            f"<li><code>{esc(e['ref'])}</code> — "
            f"<code>{esc(e['source_content_sha256'])}</code></li>"
            for e in document.provenance_index()
        ]
    else:
        return []
    return [f"<section><h2>{esc(block.heading)}</h2><ul>", *rows, "</ul></section>"]


# ---------------------------------------------------------------------------
# plaintext
# ---------------------------------------------------------------------------


def render_plaintext(document: ComposedDocument, descriptor: FormatDescriptor) -> str:
    out = [
        GENERATED_BANNER,
        "=" * 78,
        f"{document.format_label.upper()}: {document.title}",
        "=" * 78,
        "",
    ]
    for key, value in _metadata(document):
        out.append(f"{key + ':':<32}{value}")
    if descriptor.notes:
        out.extend(["", f"NOTE: {descriptor.notes}"])
    for block in document.blocks:
        if block.section_key == "title-block":
            continue
        if block.structural:
            out.extend(_plaintext_structural(document, block))
            continue
        if block.is_empty:
            continue
        out.extend(["", block.heading.upper(), "-" * len(block.heading)])
        for ordinal, resolved in enumerate(block.resolved, start=1):
            for item in _items(resolved):
                out.append(f"{ordinal}. {item}")
                out.append(f"   {_attribution(resolved)}")
    out.append("")
    return "\n".join(out)


def _plaintext_structural(document: ComposedDocument, block: ComposedBlock) -> list[str]:
    if block.section_key == "references":
        rows = [
            f"[{i}] {c.ref}  ->  {c.source_locator}"
            for i, c in enumerate(document.citations, start=1)
        ]
    elif block.section_key == "provenance":
        rows = [
            f"{e['ref']}  sha256:{e['source_content_sha256']}" for e in document.provenance_index()
        ]
    else:
        return []
    return ["", block.heading.upper(), "-" * len(block.heading), *rows]


# ---------------------------------------------------------------------------
# json
# ---------------------------------------------------------------------------


def render_json(document: ComposedDocument, descriptor: FormatDescriptor) -> str:
    payload = document.to_dict()
    payload["banner"] = GENERATED_BANNER
    payload["descriptor"] = descriptor.to_dict()
    return canonical_json(payload)


# ---------------------------------------------------------------------------
# registry
# ---------------------------------------------------------------------------

_RENDERERS: dict[str, Renderer] = {
    "markdown": render_markdown,
    "latex": render_latex,
    "html": render_html,
    "plaintext": render_plaintext,
    "json": render_json,
}


def register_renderer(renderer_id: str, renderer: Renderer) -> None:
    """Add an output syntax at runtime (the renderer space is open, like the formats)."""
    if not renderer_id or not callable(renderer):
        raise KernelError("renderer requires an id and a callable", renderer_id=renderer_id)
    _RENDERERS[renderer_id] = renderer


def renderer_ids() -> list[str]:
    return sorted(_RENDERERS)


def get_renderer(renderer_id: str) -> Renderer:
    renderer = _RENDERERS.get(renderer_id)
    if renderer is None:
        raise KernelError(
            "renderer is not registered", renderer_id=renderer_id, registered=renderer_ids()
        )
    return renderer


def render(document: ComposedDocument, descriptor: FormatDescriptor) -> str:
    """Render a composed document using the renderer its format declares."""
    return get_renderer(descriptor.renderer)(document, descriptor)


__all__ = [
    "Renderer",
    "get_renderer",
    "register_renderer",
    "render",
    "render_html",
    "render_json",
    "render_latex",
    "render_markdown",
    "render_plaintext",
    "renderer_ids",
]
