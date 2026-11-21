package composer

import (
	"crypto/sha256"
	"encoding/hex"
	"fmt"
	"os"
	"path/filepath"
	"sort"
	"strconv"
	"strings"
	"unicode/utf8"

	"go.yaml.in/yaml/v3"
)

// ---------------------------------------------------------------- registry

type Manifest struct {
	Metadata struct {
		ID             string `yaml:"id"`
		Version        string `yaml:"version"`
		Phase          int    `yaml:"phase"`
		Scope          string `yaml:"scope"`
		CapabilityKind string `yaml:"capabilityKind"`
	} `yaml:"metadata"`
	Spec struct {
		Implements []string `yaml:"implements"`
		Provides   struct {
			ObjectTypes []string `yaml:"objectTypes"`
			Events      []string `yaml:"events"`
		} `yaml:"provides"`
		Consumes struct {
			Events []string `yaml:"events"`
		} `yaml:"consumes"`
		Requires []struct {
			Capability string `yaml:"capability"`
		} `yaml:"requires"`
		Selection struct {
			Jurisdictions []string `yaml:"jurisdictions"`
			Methods       []string `yaml:"methods"`
			Realities     []string `yaml:"realities"`
		} `yaml:"selection"`
	} `yaml:"spec"`
}

type Regulation struct {
	ID           string         `yaml:"id"`
	Jurisdiction string         `yaml:"jurisdiction"`
	When         map[string]any `yaml:"when"`
	Controls     []string       `yaml:"controls"`
}

type Defaults struct {
	BaseCapabilities []string `yaml:"baseCapabilities"`
	Channels         map[string]struct {
		Capabilities     []string `yaml:"capabilities"`
		MessagingMethods []string `yaml:"messagingMethods"`
		RtcMethods       []string `yaml:"rtcMethods"`
	} `yaml:"channels"`
	AlwaysMessagingMethods []string            `yaml:"alwaysMessagingMethods"`
	DefaultPaymentMethods  map[string][]string `yaml:"defaultPaymentMethods"`
	CountryCurrency        map[string]string   `yaml:"countryCurrency"`
	AbstractMethodSource   map[string]string   `yaml:"abstractMethodSource"`
	IOAbstracts            []string            `yaml:"ioAbstracts"`
}

type PD struct {
	Metadata struct {
		ID      string `yaml:"id"`
		Version string `yaml:"version"`
	} `yaml:"metadata"`
	Spec struct {
		TargetPhase   *int     `yaml:"targetPhase"`
		Reality       string   `yaml:"reality"`
		BusinessModel []string `yaml:"businessModel"`
		Geography     struct {
			Countries       []string          `yaml:"countries"`
			PrimaryCurrency map[string]string `yaml:"primaryCurrency"`
		} `yaml:"geography"`
		Channels     []string `yaml:"channels"`
		Capabilities struct {
			Include []string `yaml:"include"`
			Exclude []string `yaml:"exclude"`
		} `yaml:"capabilities"`
		PaymentMethods map[string][]string `yaml:"paymentMethods"`
		Compliance     struct {
			Frameworks []string `yaml:"frameworks"`
		} `yaml:"compliance"`
	} `yaml:"spec"`
}

// Registry is everything composition reads, loaded from a repository checkout.
type Registry struct {
	Packs    map[string]*Manifest
	Regs     []Regulation
	Controls map[string][]string
	Defaults Defaults
	Program  *Program
}

func readYAML(path string, v any) error {
	b, err := os.ReadFile(path)
	if err != nil {
		return err
	}
	return yaml.Unmarshal(b, v)
}

// LoadRegistry reads spec/ under root.
func LoadRegistry(root string) (*Registry, error) {
	r := &Registry{Packs: map[string]*Manifest{}}
	files, _ := filepath.Glob(filepath.Join(root, "spec", "capabilities", "packs", "*.yaml"))
	for _, f := range files {
		m := &Manifest{}
		if err := readYAML(f, m); err != nil {
			return nil, fmt.Errorf("%s: %w", f, err)
		}
		r.Packs[m.Metadata.ID] = m
	}
	var regs struct {
		Regulations []Regulation `yaml:"regulations"`
	}
	if err := readYAML(filepath.Join(root, "spec", "rules", "facts", "regulations.yaml"), &regs); err != nil {
		return nil, err
	}
	r.Regs = regs.Regulations
	var ctl struct {
		Controls map[string][]string `yaml:"controls"`
	}
	if err := readYAML(filepath.Join(root, "spec", "rules", "facts", "controls.yaml"), &ctl); err != nil {
		return nil, err
	}
	r.Controls = ctl.Controls
	if err := readYAML(filepath.Join(root, "spec", "rules", "facts", "defaults.yaml"), &r.Defaults); err != nil {
		return nil, err
	}
	var text strings.Builder
	dl, _ := filepath.Glob(filepath.Join(root, "spec", "rules", "*", "*.dl"))
	sort.Strings(dl)
	for _, f := range dl {
		b, err := os.ReadFile(f)
		if err != nil {
			return nil, err
		}
		text.Write(b)
		text.WriteString("\n")
	}
	p, err := Parse(text.String())
	if err != nil {
		return nil, err
	}
	r.Program = p
	return r, nil
}

// ---------------------------------------------------------------- encoding (same facts as tools/datalog.py)

func (r *Registry) Encode(pd *PD) *DB {
	db := NewDB()
	s := pd.Spec
	var jurs []string
	for _, c := range s.Geography.Countries {
		jurs = append(jurs, "ucos:jur:"+c)
	}
	msg := map[string]bool{}
	for _, m := range r.Defaults.AlwaysMessagingMethods {
		msg[m] = true
	}
	rtc := map[string]bool{}
	for _, c := range s.Capabilities.Include {
		db.Add("requested", c)
	}
	for _, ch := range s.Channels {
		cd, ok := r.Defaults.Channels[ch]
		if !ok {
			continue
		}
		for _, c := range cd.Capabilities {
			db.Add("requested", c)
		}
		for _, m := range cd.MessagingMethods {
			msg[m] = true
		}
		for _, m := range cd.RtcMethods {
			rtc[m] = true
		}
	}
	cur := map[string]bool{}
	for _, c := range s.Geography.Countries {
		v, ok := s.Geography.PrimaryCurrency[c]
		if !ok {
			v = r.Defaults.CountryCurrency[c]
		}
		cur[v] = true
	}
	if len(cur) > 1 {
		db.Add("requested", "fx.provider")
	}
	for _, c := range r.Defaults.BaseCapabilities {
		db.Add("base_capability", c)
	}
	tp := 1
	if s.TargetPhase != nil {
		tp = *s.TargetPhase
	}
	db.Add("target_phase", strconv.Itoa(tp))
	reality := s.Reality
	if reality == "" {
		reality = "physical"
	}
	db.Add("pd_reality", reality)
	for _, c := range s.Capabilities.Exclude {
		db.Add("excluded", c)
	}
	for _, j := range jurs {
		db.Add("in_scope", j)
	}
	for _, m := range s.BusinessModel {
		db.Add("pd_business_model", m)
	}
	for _, ch := range s.Channels {
		db.Add("pd_channel", ch)
	}
	if msg["sms"] {
		db.Add("pd_channel", "sms")
	}
	for _, f := range s.Compliance.Frameworks {
		db.Add("pd_framework", f)
	}
	for _, reg := range r.Regs {
		db.Add("regulation", reg.ID, reg.Jurisdiction)
		if b, _ := reg.When["always"].(bool); b {
			db.Add("reg_when_always", reg.ID)
		}
		for k, p := range map[string]string{"capability": "reg_when_capability", "businessModel": "reg_when_business_model",
			"channel": "reg_when_channel", "framework": "reg_when_framework"} {
			if v, ok := reg.When[k].(string); ok {
				db.Add(p, reg.ID, v)
			}
		}
		for _, k := range reg.Controls {
			db.Add("requires_control", reg.ID, k)
		}
	}
	for k, cs := range r.Controls {
		for _, c := range cs {
			db.Add("control_implemented_by", k, c)
		}
	}
	sorted := func(m map[string]bool) []string {
		var out []string
		for k := range m {
			out = append(out, k)
		}
		sort.Strings(out)
		return out
	}
	for id, m := range r.Packs {
		md, sp := m.Metadata, m.Spec
		db.Add("provider_capability", id)
		db.Add("phase_of", id, strconv.Itoa(md.Phase))
		for _, q := range sp.Requires {
			db.Add("requires", id, q.Capability)
		}
		for _, e := range sp.Provides.Events {
			db.Add("provides_event", id, e)
		}
		for _, e := range sp.Consumes.Events {
			db.Add("consumes_event", id, e)
		}
		if md.CapabilityKind == "adapter" || md.CapabilityKind == "simulator" {
			db.Add("adapter_kind", id)
		}
		if md.CapabilityKind == "abstract" {
			db.Add("abstract", id)
			src := r.Defaults.AbstractMethodSource[id]
			for i, j := range jurs {
				var ms []string
				switch src {
				case "paymentMethods":
					pm, ok := s.PaymentMethods[s.Geography.Countries[i]]
					if !ok {
						pm = r.Defaults.DefaultPaymentMethods[s.Geography.Countries[i]]
					}
					ms = pm
				case "messagingMethods":
					ms = sorted(msg)
				case "rtcMethods":
					ms = sorted(rtc)
				default:
					ms = []string{"-"}
				}
				for _, mth := range ms {
					db.Add("needed_method", id, j, mth)
				}
			}
		}
		for _, a := range sp.Implements {
			db.Add("implements", id, a)
			if md.CapabilityKind == "simulator" {
				db.Add("simulator_for", id, a)
			}
		}
		if len(sp.Implements) > 0 {
			js := sp.Selection.Jurisdictions
			if len(js) == 0 {
				js = []string{"*"}
			}
			for _, j := range js {
				db.Add("adapter_jur", id, j)
			}
			for _, mth := range sp.Selection.Methods {
				db.Add("adapter_method", id, mth)
			}
			rs := sp.Selection.Realities
			if len(rs) == 0 {
				rs = []string{"physical"}
			}
			for _, x := range rs {
				db.Add("adapter_reality", id, x)
			}
		}
	}
	for _, a := range r.Defaults.IOAbstracts {
		db.Add("io_abstract", a)
	}
	return db
}

// ---------------------------------------------------------------- composition

var severity = map[string]string{
	"MISSING_CAPABILITY": "MANDATORY", "CONFLICT_EXCLUDED": "MANDATORY", "PHASE_NOT_AVAILABLE": "MANDATORY",
	"MISSING_ADAPTER": "MANDATORY", "CONTROL_NOT_IMPLEMENTED": "MANDATORY",
	"MISSING_SIMULATOR": "RECOMMENDED", "EVENT_WITHOUT_PRODUCER_IN_BLUEPRINT": "RECOMMENDED",
}

// Gap is one finding of the gap report (severity, kind, subject).
type Gap struct{ Severity, Kind, Subject string }

// Result is a composed blueprint, its gaps and the provenance of every derived fact.
type Result struct {
	Blueprint map[string]any
	ID        string
	Gaps      []Gap
	Proof     map[string]string
	Facts     int
}

// Compose evaluates the rules for pd with the choice() loop for adapters (closure.dl) and assembles the blueprint.
func (r *Registry) Compose(pd *PD) (*Result, error) {
	chosen := map[[3]string]string{}
	var db *DB
	for round := 0; round < 50; round++ {
		db = r.Encode(pd)
		for k, a := range chosen {
			db.Add("chosen_adapter", k[0], k[1], k[2], a)
		}
		if err := r.Program.Evaluate(db); err != nil {
			return nil, err
		}
		next := map[[3]string]string{}
		rank := map[[3]string][2]string{}
		for _, t := range db.Facts("selected_adapter") {
			k := [3]string{t[0], t[1], t[2]}
			spec := "1"
			if db.Has("adapter_jur", t[3], t[1]) {
				spec = "0"
			}
			cand := [2]string{spec, t[3]}
			if cur, ok := rank[k]; !ok || cand[0] < cur[0] || (cand[0] == cur[0] && cand[1] < cur[1]) {
				rank[k] = cand
				next[k] = t[3]
			}
		}
		if equalChoice(next, chosen) {
			break
		}
		chosen = next
	}
	required := map[string]bool{}
	for _, t := range db.Facts("required") {
		if _, ok := r.Packs[t[0]]; ok {
			required[t[0]] = true
		}
	}
	ids := sortedKeys(required)
	applies := map[string]bool{}
	for _, t := range db.Facts("applies") {
		applies[t[0]] = true
	}
	controls := map[string]map[string]bool{}
	for _, t := range db.Facts("requires_control") {
		if applies[t[0]] {
			if controls[t[1]] == nil {
				controls[t[1]] = map[string]bool{}
			}
			controls[t[1]][t[0]] = true
		}
	}
	caps := []any{}
	objTypes, events := []string{}, map[string]bool{}
	for _, c := range ids {
		m := r.Packs[c]
		caps = append(caps, map[string]any{"id": c, "version": m.Metadata.Version, "scope": m.Metadata.Scope})
		objTypes = append(objTypes, m.Spec.Provides.ObjectTypes...)
		for _, e := range m.Spec.Provides.Events {
			events[e] = true
		}
	}
	sort.Strings(objTypes)
	var keys [][3]string
	for k := range chosen {
		keys = append(keys, k)
	}
	sort.Slice(keys, func(i, j int) bool {
		a, b := keys[i], keys[j]
		if a[0] != b[0] {
			return a[0] < b[0]
		}
		if a[1] != b[1] {
			return a[1] < b[1]
		}
		return a[2] < b[2]
	})
	adapters := []any{}
	for _, k := range keys {
		adapters = append(adapters, map[string]any{"abstract": k[0], "jurisdiction": k[1], "method": k[2], "implementation": chosen[k]})
	}
	ctlList := []any{}
	for _, k := range sortedKeys(controlsKeys(controls)) {
		impl := []any{}
		for _, c := range r.Controls[k] {
			impl = append(impl, c)
		}
		ctlList = append(ctlList, map[string]any{"control": k, "regulations": toAny(sortedKeys(controls[k])), "implementedBy": impl})
	}
	tp := 1
	if pd.Spec.TargetPhase != nil {
		tp = *pd.Spec.TargetPhase
	}
	bp := map[string]any{
		"kind": "Blueprint", "platformDefinition": pd.Metadata.ID + "@" + pd.Metadata.Version, "targetPhase": tp,
		"capabilities": caps, "adapters": adapters, "controls": ctlList,
		"objectTypes": toAny(objTypes), "events": toAny(sortedKeys(events)),
	}
	if pd.Spec.Reality != "" && pd.Spec.Reality != "physical" {
		bp["reality"] = pd.Spec.Reality
	}
	sum := sha256.Sum256(Canonical(bp))
	id := "ucos:blueprint:sha256:" + hex.EncodeToString(sum[:])
	bp["id"] = id
	gapSet := map[Gap]bool{}
	for _, t := range db.Facts("gap") {
		gapSet[Gap{severity[t[0]], t[0], t[1]}] = true
	}
	var gaps []Gap
	for g := range gapSet {
		gaps = append(gaps, g)
	}
	sort.Slice(gaps, func(i, j int) bool {
		return gaps[i].Severity+gaps[i].Kind+gaps[i].Subject < gaps[j].Severity+gaps[j].Kind+gaps[j].Subject
	})
	return &Result{Blueprint: bp, ID: id, Gaps: gaps, Proof: db.Proof, Facts: db.Count()}, nil
}

func equalChoice(a, b map[[3]string]string) bool {
	if len(a) != len(b) {
		return false
	}
	for k, v := range a {
		if b[k] != v {
			return false
		}
	}
	return true
}

func controlsKeys(m map[string]map[string]bool) map[string]bool {
	out := map[string]bool{}
	for k := range m {
		out[k] = true
	}
	return out
}

func sortedKeys(m map[string]bool) []string {
	out := make([]string, 0, len(m))
	for k := range m {
		out = append(out, k)
	}
	sort.Strings(out)
	return out
}

func toAny(xs []string) []any {
	out := make([]any, len(xs))
	for i, x := range xs {
		out[i] = x
	}
	return out
}

// Canonical serialises like Python's json.dumps(v, sort_keys=True, separators=(',', ':')): sorted keys, no spaces,
// non-ASCII escaped as \uXXXX (surrogate pairs above U+FFFF).
func Canonical(v any) []byte {
	var b strings.Builder
	writeCanonical(&b, v)
	return []byte(b.String())
}

func writeCanonical(b *strings.Builder, v any) {
	switch x := v.(type) {
	case nil:
		b.WriteString("null")
	case bool:
		if x {
			b.WriteString("true")
		} else {
			b.WriteString("false")
		}
	case int:
		b.WriteString(strconv.Itoa(x))
	case int64:
		b.WriteString(strconv.FormatInt(x, 10))
	case float64:
		if x == float64(int64(x)) {
			b.WriteString(strconv.FormatInt(int64(x), 10))
		} else {
			b.WriteString(strconv.FormatFloat(x, 'g', -1, 64))
		}
	case string:
		writeString(b, x)
	case []any:
		b.WriteByte('[')
		for i, e := range x {
			if i > 0 {
				b.WriteByte(',')
			}
			writeCanonical(b, e)
		}
		b.WriteByte(']')
	case []string:
		writeCanonical(b, toAny(x))
	case map[string]any:
		ks := make([]string, 0, len(x))
		for k := range x {
			ks = append(ks, k)
		}
		sort.Strings(ks)
		b.WriteByte('{')
		for i, k := range ks {
			if i > 0 {
				b.WriteByte(',')
			}
			writeString(b, k)
			b.WriteByte(':')
			writeCanonical(b, x[k])
		}
		b.WriteByte('}')
	default:
		panic(fmt.Sprintf("composer: cannot canonicalise %T", v))
	}
}

func writeString(b *strings.Builder, s string) {
	b.WriteByte('"')
	for _, r := range s {
		switch {
		case r == '"':
			b.WriteString(`\"`)
		case r == '\\':
			b.WriteString(`\\`)
		case r == '\n':
			b.WriteString(`\n`)
		case r == '\r':
			b.WriteString(`\r`)
		case r == '\t':
			b.WriteString(`\t`)
		case r == '\b':
			b.WriteString(`\b`)
		case r == '\f':
			b.WriteString(`\f`)
		case r < 0x20 || (r > 0x7e && r <= 0xffff):
			fmt.Fprintf(b, `\u%04x`, r)
		case r > 0xffff:
			r -= 0x10000
			fmt.Fprintf(b, `\u%04x\u%04x`, 0xd800+(r>>10), 0xdc00+(r&0x3ff))
		default:
			b.WriteRune(r)
		}
	}
	b.WriteByte('"')
	_ = utf8.RuneError
}
