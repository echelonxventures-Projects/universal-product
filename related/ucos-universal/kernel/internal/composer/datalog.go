// Package composer is the composition engine (U58, ADR-022): an embedded, stratified, semi-naive Datalog
// evaluator for spec/rules/**/*.dl with provenance, plus blueprint assembly. Its results must equal those of
// the reference checker (tools/ucos_check.py) byte for byte; the golden platforms are its acceptance tests.
package composer

import (
	"fmt"
	"regexp"
	"sort"
	"strconv"
	"strings"
)

// ---------------------------------------------------------------- program model

type termKind int

const (
	tConst termKind = iota
	tVar
	tAny
)

type term struct {
	kind termKind
	val  string // constant value or variable name
}

type litKind int

const (
	lPos litKind = iota
	lNeg
	lCmp
	lOr
)

type literal struct {
	kind  litKind
	pred  string
	args  []term
	op    string // for lCmp
	l, r  term
	alts  []literal // for lOr
	label string    // source text, for provenance
	vs    []string  // variables, computed once
}

type rule struct {
	head literal
	body []literal
	text string
}

// Program is a parsed rule set with its predicate declarations (name -> arity).
type Program struct {
	Decls map[string]int
	Rules []rule
}

var (
	commentRe = regexp.MustCompile(`//[^\n]*`)
	declRe    = regexp.MustCompile(`\.decl\s+([a-z_][a-z0-9_]*)\s*\(([^)]*)\)`)
	declLine  = regexp.MustCompile(`\.decl[^\n]*`)
	stmtSplit = regexp.MustCompile(`\.\s*(?:\n|$)`)
	cmpRe     = regexp.MustCompile(`^("[^"]*"|-?\d+|[A-Za-z_][A-Za-z0-9_]*)\s*(<=|>=|!=|=|<|>)\s*("[^"]*"|-?\d+|[A-Za-z_][A-Za-z0-9_]*)$`)
	atomRe    = regexp.MustCompile(`(?s)^(!?)\s*([a-z_][a-z0-9_]*)\s*\((.*)\)$`)
)

func splitTop(s string, sep rune) []string {
	var out []string
	depth, inQ, cur := 0, false, strings.Builder{}
	for _, ch := range s {
		if ch == '"' {
			inQ = !inQ
		}
		if !inQ {
			if ch == '(' {
				depth++
			} else if ch == ')' {
				depth--
			}
		}
		if ch == sep && depth == 0 && !inQ {
			out = append(out, strings.TrimSpace(cur.String()))
			cur.Reset()
			continue
		}
		cur.WriteRune(ch)
	}
	if strings.TrimSpace(cur.String()) != "" {
		out = append(out, strings.TrimSpace(cur.String()))
	}
	return out
}

func parseTerm(s string) term {
	s = strings.TrimSpace(s)
	switch {
	case strings.HasPrefix(s, `"`):
		return term{tConst, strings.Trim(s, `"`)}
	case s == "_":
		return term{tAny, ""}
	case regexp.MustCompile(`^-?\d+$`).MatchString(s):
		return term{tConst, s}
	default:
		return term{tVar, s}
	}
}

func parseLiteral(s string) (literal, error) {
	s = strings.TrimSpace(s)
	if strings.HasPrefix(s, "(") && strings.HasSuffix(s, ")") {
		if parts := splitTop(s[1:len(s)-1], ';'); len(parts) > 1 {
			l := literal{kind: lOr, label: s}
			for _, p := range parts {
				a, err := parseLiteral(p)
				if err != nil {
					return l, err
				}
				l.alts = append(l.alts, a)
			}
			return l, nil
		}
	}
	if m := cmpRe.FindStringSubmatch(s); m != nil {
		return literal{kind: lCmp, op: m[2], l: parseTerm(m[1]), r: parseTerm(m[3]), label: s}, nil
	}
	m := atomRe.FindStringSubmatch(s)
	if m == nil {
		return literal{}, fmt.Errorf("composer: cannot parse literal %q", s)
	}
	l := literal{kind: lPos, pred: m[2], label: s}
	if m[1] == "!" {
		l.kind = lNeg
	}
	for _, a := range splitTop(m[3], ',') {
		l.args = append(l.args, parseTerm(a))
	}
	return l, nil
}

func (l *literal) prepare() {
	for i := range l.alts {
		l.alts[i].prepare()
	}
	for v := range vars(*l) {
		l.vs = append(l.vs, v)
	}
}

// Parse reads the Souffle subset used by spec/rules.
func Parse(text string) (*Program, error) {
	text = commentRe.ReplaceAllString(text, "")
	p := &Program{Decls: map[string]int{}}
	for _, m := range declRe.FindAllStringSubmatch(text, -1) {
		n := 0
		for _, a := range strings.Split(m[2], ",") {
			if strings.TrimSpace(a) != "" {
				n++
			}
		}
		p.Decls[m[1]] = n
	}
	body := declLine.ReplaceAllString(text, "")
	for _, stmt := range stmtSplit.Split(body, -1) {
		stmt = strings.TrimSpace(stmt)
		if stmt == "" {
			continue
		}
		head, rhs, ok := strings.Cut(stmt, ":-")
		if !ok {
			return nil, fmt.Errorf("composer: not a rule: %q", stmt)
		}
		h, err := parseLiteral(head)
		if err != nil {
			return nil, err
		}
		r := rule{head: h, text: stmt}
		for _, b := range splitTop(rhs, ',') {
			l, err := parseLiteral(b)
			if err != nil {
				return nil, err
			}
			l.prepare()
			r.body = append(r.body, l)
		}
		r.head.prepare()
		p.Rules = append(p.Rules, r)
	}
	return p, nil
}

// ---------------------------------------------------------------- relations with indexes

// Tuple is a fact's arguments; numbers are decimal strings.
type Tuple []string

func key(t Tuple) string { return strings.Join(t, "\x1f") }

type relation struct {
	tuples []Tuple
	set    map[string]int           // key -> index
	index  map[int]map[string][]int // argument position -> value -> tuple indexes
}

func newRelation() *relation {
	return &relation{set: map[string]int{}, index: map[int]map[string][]int{}}
}

func (r *relation) add(t Tuple) bool {
	k := key(t)
	if _, ok := r.set[k]; ok {
		return false
	}
	r.set[k] = len(r.tuples)
	r.tuples = append(r.tuples, t)
	for pos, idx := range r.index {
		idx[t[pos]] = append(idx[t[pos]], len(r.tuples)-1)
	}
	return true
}

func (r *relation) lookup(pos int, v string) []int {
	idx, ok := r.index[pos]
	if !ok {
		idx = map[string][]int{}
		for i, t := range r.tuples {
			idx[t[pos]] = append(idx[t[pos]], i)
		}
		r.index[pos] = idx
	}
	return idx[v]
}

// DB holds relations and, for derived facts, the rule that first derived them (provenance).
type DB struct {
	rels  map[string]*relation
	Proof map[string]string // "pred(key)" -> rule text
}

func NewDB() *DB { return &DB{rels: map[string]*relation{}, Proof: map[string]string{}} }

func (db *DB) rel(p string) *relation {
	r, ok := db.rels[p]
	if !ok {
		r = newRelation()
		db.rels[p] = r
	}
	return r
}

// Add inserts an EDB fact.
func (db *DB) Add(pred string, t ...string) { db.rel(pred).add(Tuple(t)) }

// Facts returns a predicate's tuples (do not modify).
func (db *DB) Facts(pred string) []Tuple { return db.rel(pred).tuples }

// Has reports whether the fact exists.
func (db *DB) Has(pred string, t ...string) bool { _, ok := db.rel(pred).set[key(t)]; return ok }

// Count returns the number of facts across all predicates.
func (db *DB) Count() int {
	n := 0
	for _, r := range db.rels {
		n += len(r.tuples)
	}
	return n
}

// ---------------------------------------------------------------- evaluation

type env map[string]string

func val(t term, e env) (string, bool) {
	switch t.kind {
	case tConst:
		return t.val, true
	case tVar:
		v, ok := e[t.val]
		return v, ok
	}
	return "", false
}

func vars(l literal) map[string]bool {
	out := map[string]bool{}
	switch l.kind {
	case lPos, lNeg:
		for _, a := range l.args {
			if a.kind == tVar {
				out[a.val] = true
			}
		}
	case lCmp:
		for _, a := range []term{l.l, l.r} {
			if a.kind == tVar {
				out[a.val] = true
			}
		}
	case lOr:
		for _, a := range l.alts {
			for v := range vars(a) {
				out[v] = true
			}
		}
	}
	return out
}

func compare(op, a, b string) bool {
	ai, e1 := strconv.ParseInt(a, 10, 64)
	bi, e2 := strconv.ParseInt(b, 10, 64)
	if e1 == nil && e2 == nil {
		switch op {
		case "=":
			return ai == bi
		case "!=":
			return ai != bi
		case "<":
			return ai < bi
		case "<=":
			return ai <= bi
		case ">":
			return ai > bi
		case ">=":
			return ai >= bi
		}
	}
	switch op {
	case "=":
		return a == b
	case "!=":
		return a != b
	case "<":
		return a < b
	case "<=":
		return a <= b
	case ">":
		return a > b
	case ">=":
		return a >= b
	}
	return false
}

// match finds tuples of rel matching the atom under e, using the first bound argument's index.
func (db *DB) match(l literal, e env, src *relation, emit func(env, Tuple)) {
	if src == nil {
		src = db.rel(l.pred)
	}
	candidates := []int(nil)
	scanned := false
	for pos, a := range l.args {
		if v, ok := val(a, e); ok {
			candidates = src.lookup(pos, v)
			scanned = true
			break
		}
	}
	try := func(t Tuple) {
		ne := e
		copied := false
		for pos, a := range l.args {
			switch a.kind {
			case tConst:
				if t[pos] != a.val {
					return
				}
			case tVar:
				if v, ok := ne[a.val]; ok {
					if v != t[pos] {
						return
					}
					continue
				}
				if !copied {
					ne = make(env, len(e)+2)
					for k, v := range e {
						ne[k] = v
					}
					copied = true
				}
				ne[a.val] = t[pos]
			}
		}
		emit(ne, t)
	}
	if scanned {
		for _, i := range candidates {
			try(src.tuples[i])
		}
		return
	}
	for _, t := range src.tuples {
		try(t)
	}
}

// solve enumerates bindings for body under e. deltaAt selects one positive literal to read from delta.
type fact struct {
	pred string
	t    Tuple
}

func (db *DB) solve(body []literal, e env, deltaAt int, delta map[string]*relation, support []fact, out func(env, []fact)) {
	if len(body) == 0 {
		out(e, support)
		return
	}
	// Join order: the delta literal first; then any filter (negation, comparison, disjunction) whose variables are
	// all bound; then the positive atom with the most bound arguments (smallest relation on ties). A disjunction
	// waits until its variables are bound, as in the reference evaluator.
	pick := -1
	if deltaAt >= 0 && deltaAt < len(body) && body[deltaAt].kind == lPos {
		pick = deltaAt
	}
	if pick < 0 {
		for i, l := range body {
			if l.kind == lPos {
				continue
			}
			ready := true
			for _, v := range l.vs {
				if _, ok := e[v]; !ok {
					ready = false
					break
				}
			}
			if ready {
				pick = i
				break
			}
		}
	}
	if pick < 0 {
		best, bestSize := -1, 0
		for i, l := range body {
			if l.kind != lPos {
				continue
			}
			bound := 0
			for _, a := range l.args {
				if _, ok := val(a, e); ok {
					bound++
				}
			}
			size := len(db.rel(l.pred).tuples)
			if pick < 0 || bound > best || (bound == best && size < bestSize) {
				pick, best, bestSize = i, bound, size
			}
		}
	}
	if pick < 0 { // only filters with unbound variables remain: evaluate them in order (reference semantics)
		pick = 0
	}
	l := body[pick]
	rest := append(append([]literal{}, body[:pick]...), body[pick+1:]...)
	nextDelta := deltaAt
	if deltaAt == pick {
		nextDelta = -1
	} else if deltaAt > pick {
		nextDelta = deltaAt - 1
	}
	switch l.kind {
	case lPos:
		var src *relation
		if deltaAt == pick {
			src = delta[l.pred]
			if src == nil {
				return
			}
		}
		db.match(l, e, src, func(ne env, t Tuple) {
			db.solve(rest, ne, nextDelta, delta, append(support[:len(support):len(support)], fact{l.pred, t}), out)
		})
	case lNeg:
		found := false
		db.match(l, e, nil, func(env, Tuple) { found = true })
		if !found {
			db.solve(rest, e, nextDelta, delta, support, out)
		}
	case lCmp:
		a, ok1 := val(l.l, e)
		b, ok2 := val(l.r, e)
		if ok1 && ok2 && compare(l.op, a, b) {
			db.solve(rest, e, nextDelta, delta, support, out)
		}
	case lOr:
		for _, alt := range l.alts {
			db.solve(append([]literal{alt}, rest...), e, func() int {
				if nextDelta >= 0 {
					return nextDelta + 1
				}
				return -1
			}(), delta, support, out)
		}
	}
}

// strata assigns each derived predicate a stratum so negation only reads completed strata.
func (p *Program) strata() (map[string]int, error) {
	level := map[string]int{}
	for _, r := range p.Rules {
		level[r.head.pred] = 0
	}
	deps := func(l literal, f func(pred string, neg bool)) {
		if l.kind == lOr {
			for _, a := range l.alts {
				if a.kind == lPos || a.kind == lNeg {
					f(a.pred, a.kind == lNeg)
				}
			}
		} else if l.kind == lPos || l.kind == lNeg {
			f(l.pred, l.kind == lNeg)
		}
	}
	for i := 0; i <= len(level)+1; i++ {
		changed := false
		for _, r := range p.Rules {
			for _, l := range r.body {
				deps(l, func(pred string, neg bool) {
					lv, derived := level[pred]
					if !derived {
						return
					}
					need := lv
					if neg {
						need++
					}
					if level[r.head.pred] < need {
						level[r.head.pred] = need
						changed = true
					}
				})
			}
		}
		if !changed {
			return level, nil
		}
	}
	return nil, fmt.Errorf("composer: rules are not stratifiable")
}

// Evaluate computes all derived facts into db (semi-naive per stratum) and records provenance.
func (p *Program) Evaluate(db *DB) error {
	level, err := p.strata()
	if err != nil {
		return err
	}
	var ls []int
	seen := map[int]bool{}
	for _, l := range level {
		if !seen[l] {
			seen[l] = true
			ls = append(ls, l)
		}
	}
	sort.Ints(ls)
	for _, s := range ls {
		var rules []rule
		for _, r := range p.Rules {
			if level[r.head.pred] == s {
				rules = append(rules, r)
			}
		}
		inStratum := map[string]bool{}
		for _, r := range rules {
			inStratum[r.head.pred] = true
		}
		derive := func(r rule, deltaAt int, delta map[string]*relation, next map[string]*relation) {
			db.solve(r.body, env{}, deltaAt, delta, nil, func(e env, support []fact) {
				t := make(Tuple, len(r.head.args))
				for i, a := range r.head.args {
					v, _ := val(a, e)
					t[i] = v
				}
				if db.rel(r.head.pred).add(t) {
					parts := make([]string, len(support))
					for i, s := range support {
						parts[i] = s.pred + "(" + strings.Join(s.t, ", ") + ")"
					}
					db.Proof[r.head.pred+"("+strings.Join(t, ", ")+")"] = r.text + "  <=  " + strings.Join(parts, ", ")
					if next[r.head.pred] == nil {
						next[r.head.pred] = newRelation()
					}
					next[r.head.pred].add(t)
				}
			})
		}
		// First round: every rule over full relations.
		delta := map[string]*relation{}
		for _, r := range rules {
			derive(r, -1, nil, delta)
		}
		// Later rounds: only rules with a positive literal of this stratum, reading that literal from delta.
		for len(delta) > 0 {
			next := map[string]*relation{}
			for _, r := range rules {
				for i, l := range r.body {
					if l.kind == lPos && inStratum[l.pred] && delta[l.pred] != nil {
						derive(r, i, delta, next)
					}
					if l.kind == lOr {
						for _, a := range l.alts {
							if a.kind == lPos && inStratum[a.pred] && delta[a.pred] != nil {
								derive(r, -1, nil, next) // rare: disjunction over a recursive predicate
							}
						}
					}
				}
			}
			delta = next
		}
	}
	return nil
}
