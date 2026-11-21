package money

import (
	"bufio"
	"math/rand"
	"os"
	"regexp"
	"strconv"
	"testing"
)

func TestParseAndString(t *testing.T) {
	cases := []struct{ in, cur, out string }{
		{"1598.00", "INR", "1598.00"}, {"0.5", "AED", "0.50"}, {"-3.125", "KWD", "-3.125"}, {"1200", "JPY", "1200"}, {"7", "USD", "7.00"},
	}
	for _, c := range cases {
		m, err := Parse(c.in, c.cur)
		if err != nil {
			t.Fatalf("Parse(%q,%s): %v", c.in, c.cur, err)
		}
		if m.String() != c.out {
			t.Errorf("Parse(%q,%s).String() = %s, want %s", c.in, c.cur, m, c.out)
		}
	}
	for _, bad := range [][2]string{{"1.001", "INR"}, {"1.5", "JPY"}, {"abc", "INR"}, {"1", "XYZ"}, {"", "INR"}} {
		if _, err := Parse(bad[0], bad[1]); err == nil {
			t.Errorf("accepted %v", bad)
		}
	}
}

func TestAllocateExample(t *testing.T) {
	total, _ := Parse("100.00", "INR")
	got, err := Allocate(total, []int64{1, 1, 1})
	if err != nil {
		t.Fatal(err)
	}
	want := []string{"33.34", "33.33", "33.33"}
	for i := range got {
		if got[i].String() != want[i] {
			t.Fatalf("share %d = %s, want %s", i, got[i], want[i])
		}
	}
}

// ARCH-CUR-02: allocation conserves the total exactly over many random cases (1,000,000 with -long).
func TestAllocateConservesProperty(t *testing.T) {
	n := 100000
	if os.Getenv("UCOS_LONG") != "" {
		n = 1000000
	}
	rnd := rand.New(rand.NewSource(42))
	curs := []string{"INR", "JPY", "KWD"}
	for i := 0; i < n; i++ {
		total := Money{Minor: rnd.Int63n(2_000_000_000_000) - 1_000_000_000_000, Currency: curs[i%3]}
		k := 1 + rnd.Intn(12)
		w := make([]int64, k)
		var sum int64
		for j := range w {
			w[j] = rnd.Int63n(1_000_000)
			sum += w[j]
		}
		if sum == 0 {
			w[0], sum = 1, 1
		}
		shares, err := Allocate(total, w)
		if err != nil {
			t.Fatal(err)
		}
		var got int64
		for _, s := range shares {
			got += s.Minor
		}
		if got != total.Minor {
			t.Fatalf("case %d: shares sum %d != total %d", i, got, total.Minor)
		}
	}
}

func TestMinorUnitsMatchSeed(t *testing.T) {
	f, err := os.Open("../../../spec/seed/refdata/iso4217.yaml")
	if err != nil {
		t.Skip("seed not available:", err)
	}
	defer f.Close()
	alpha := regexp.MustCompile(`^- alpha3: ([A-Z]{3})$`)
	minor := regexp.MustCompile(`^  minorUnit: (\d+)$`)
	seed, cur := map[string]int{}, ""
	sc := bufio.NewScanner(f)
	for sc.Scan() {
		if m := alpha.FindStringSubmatch(sc.Text()); m != nil {
			cur = m[1]
		} else if m := minor.FindStringSubmatch(sc.Text()); m != nil && cur != "" {
			seed[cur], _ = strconv.Atoi(m[1])
		}
	}
	for c, u := range MinorUnits {
		if seed[c] != u {
			t.Errorf("%s: code has %d minor units, seed has %d", c, u, seed[c])
		}
	}
}
