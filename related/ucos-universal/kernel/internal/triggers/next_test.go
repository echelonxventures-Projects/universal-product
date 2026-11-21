package triggers

import (
	"testing"
	"time"
)

func TestNextDailyKeepsLocalTime(t *testing.T) {
	prev := time.Date(2027, 3, 27, 9, 0, 0, 0, time.UTC) // 09:00 GMT in London
	next, rec, err := Next("FREQ=DAILY;BYHOUR=9;BYMINUTE=0", "Europe/London", prev)
	if err != nil || !rec {
		t.Fatal(err)
	}
	if want := time.Date(2027, 3, 28, 8, 0, 0, 0, time.UTC); !next.Equal(want) { // 09:00 BST
		t.Fatalf("next = %s, want %s", next.UTC(), want)
	}
	if _, rec, err := Next("", "", prev); rec || err != nil {
		t.Fatal("empty rule is a one-off trigger")
	}
	for _, bad := range []string{"FREQ=WEEKLY;BYDAY=MO", "FREQ=DAILY;BYHOUR=25;BYMINUTE=0", "FREQ=DAILY;BYHOUR=9"} {
		if _, _, err := Next(bad, "Europe/London", prev); err == nil {
			t.Errorf("accepted %q", bad)
		}
	}
}
