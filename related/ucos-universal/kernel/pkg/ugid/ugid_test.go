package ugid

import (
	"sort"
	"testing"
	"time"
)

func TestNewIsValidAndSortsByTime(t *testing.T) {
	base := time.Date(2027, 1, 10, 9, 0, 0, 0, time.UTC)
	var ids []string
	for i := 0; i < 1000; i++ {
		id, err := New("order", base.Add(time.Duration(i)*time.Millisecond))
		if err != nil {
			t.Fatal(err)
		}
		if !Valid(id) {
			t.Fatalf("not valid: %s", id)
		}
		ids = append(ids, id)
	}
	if !sort.StringsAreSorted(ids) {
		t.Fatal("ids created later must sort later (time prefix)")
	}
	if k, _ := Kind(ids[0]); k != "order" {
		t.Fatalf("kind = %q", k)
	}
}

func TestValidRejects(t *testing.T) {
	for _, s := range []string{"", "order:01J", "ucos:Order:01JZ0000000000000000000000", "ucos:order:has space", "ucos:order:"} {
		if Valid(s) {
			t.Errorf("accepted %q", s)
		}
	}
	if _, err := New("Bad Kind", time.Now()); err == nil {
		t.Error("accepted invalid kind")
	}
	if !Valid("ucos:jur:IN-KA") {
		t.Error("hierarchical names are valid UGIDs")
	}
}
