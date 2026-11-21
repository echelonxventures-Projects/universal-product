package composer

import (
	"bufio"
	"encoding/json"
	"os"
	"path/filepath"
	"sort"
	"strings"
	"testing"
	"time"

	"go.yaml.in/yaml/v3"
)

const root = "../../.."

// ADR-022 / spike S-01 acceptance: the Go engine reproduces every golden blueprint byte for byte (same id) and
// the same gaps as the reference checker.
func TestGoldenBlueprintsIdentical(t *testing.T) {
	reg, err := LoadRegistry(root)
	if err != nil {
		t.Fatal(err)
	}
	pds, _ := filepath.Glob(filepath.Join(root, "spec", "composition", "golden", "*.pd.yaml"))
	if len(pds) < 5 {
		t.Fatalf("expected the golden platform definitions, found %d", len(pds))
	}
	for _, f := range pds {
		name := strings.TrimSuffix(filepath.Base(f), ".pd.yaml")
		t.Run(name, func(t *testing.T) {
			var pd PD
			b, _ := os.ReadFile(f)
			if err := yaml.Unmarshal(b, &pd); err != nil {
				t.Fatal(err)
			}
			res, err := reg.Compose(&pd)
			if err != nil {
				t.Fatal(err)
			}
			var exp map[string]any
			eb, _ := os.ReadFile(filepath.Join(root, "spec", "composition", "golden", "expected", name+".blueprint.json"))
			if err := json.Unmarshal(eb, &exp); err != nil {
				t.Fatal(err)
			}
			if res.ID != exp["id"] {
				delete(exp, "id")
				got := res.Blueprint
				for k := range exp {
					if string(Canonical(exp[k])) != string(Canonical(got[k])) {
						t.Errorf("field %s differs:\n got  %s\n want %s", k, trunc(Canonical(got[k])), trunc(Canonical(exp[k])))
					}
				}
				t.Fatalf("blueprint id %s, want %s", res.ID, exp["id"])
			}
			var gr struct {
				Gaps []struct{ Severity, Kind, Subject string } `json:"gaps"`
			}
			gb, _ := os.ReadFile(filepath.Join(root, "spec", "composition", "golden", "expected", name+".gaps.json"))
			_ = json.Unmarshal(gb, &gr)
			want := map[Gap]bool{}
			for _, g := range gr.Gaps {
				want[Gap{g.Severity, g.Kind, g.Subject}] = true
			}
			got := map[Gap]bool{}
			for _, g := range res.Gaps {
				got[g] = true
			}
			if len(got) != len(want) {
				t.Fatalf("gaps %v, want %v", res.Gaps, gr.Gaps)
			}
			for g := range want {
				if !got[g] {
					t.Fatalf("missing gap %v", g)
				}
			}
		})
	}
}

// Every derived fact carries the rule that produced it (provenance for the "Why?" view, W5).
func TestProvenanceRecorded(t *testing.T) {
	reg, err := LoadRegistry(root)
	if err != nil {
		t.Fatal(err)
	}
	var pd PD
	b, _ := os.ReadFile(filepath.Join(root, "spec", "composition", "golden", "d2c-in-ae.pd.yaml"))
	_ = yaml.Unmarshal(b, &pd)
	res, err := reg.Compose(&pd)
	if err != nil {
		t.Fatal(err)
	}
	why, ok := res.Proof["required(tax.gst-india)"]
	if !ok || !strings.Contains(why, ":-") {
		t.Fatalf("no provenance for required(tax.gst-india): %q", why)
	}
}

func trunc(b []byte) string {
	if len(b) > 300 {
		return string(b[:300]) + "…"
	}
	return string(b)
}

// Spike S-01 performance: set UCOS_S01_FACTS to a directory written by `tools/datalog.py synth 125000 <dir>`
// (~1M facts). Cold evaluation must finish in under 10 seconds.
func TestSyntheticMillionFacts(t *testing.T) {
	dir := os.Getenv("UCOS_S01_FACTS")
	if dir == "" {
		t.Skip("UCOS_S01_FACTS not set")
	}
	reg, err := LoadRegistry(root)
	if err != nil {
		t.Fatal(err)
	}
	db := NewDB()
	files, _ := filepath.Glob(filepath.Join(dir, "*.facts"))
	sort.Strings(files)
	for _, f := range files {
		pred := strings.TrimSuffix(filepath.Base(f), ".facts")
		fh, err := os.Open(f)
		if err != nil {
			t.Fatal(err)
		}
		sc := bufio.NewScanner(fh)
		sc.Buffer(make([]byte, 1<<20), 1<<20)
		for sc.Scan() {
			if line := sc.Text(); line != "" {
				db.Add(pred, strings.Split(line, "\t")...)
			}
		}
		fh.Close()
	}
	edb := db.Count()
	start := time.Now()
	if err := reg.Program.Evaluate(db); err != nil {
		t.Fatal(err)
	}
	took := time.Since(start)
	t.Logf("S-01: %d input facts, %d after evaluation, %s", edb, db.Count(), took)
	if edb < 750000 && os.Getenv("UCOS_S01_ANY") == "" {
		t.Fatalf("expected about 1M input facts, got %d", edb)
	}
	if took > 10*time.Second {
		t.Fatalf("evaluation took %s, target < 10 s", took)
	}
}
