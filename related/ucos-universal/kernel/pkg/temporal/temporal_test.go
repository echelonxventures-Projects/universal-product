package temporal

import (
	"testing"
	"time"
)

func mustLoad(t *testing.T, name string) *time.Location {
	t.Helper()
	l, err := time.LoadLocation(name)
	if err != nil {
		t.Fatal(err)
	}
	return l
}

// Same case as spec/acceptance/p0-exit/temporal-triggers.feature "A business-time deadline skips holidays".
func TestAddBusinessSkipsHoliday(t *testing.T) {
	ist := mustLoad(t, "Asia/Kolkata")
	nineToSix := Hours{Open: 9 * time.Hour, Close: 18 * time.Hour}
	cal := BusinessCalendar{Location: ist,
		Week:     map[time.Weekday]Hours{time.Monday: nineToSix, time.Tuesday: nineToSix, time.Wednesday: nineToSix, time.Thursday: nineToSix, time.Friday: nineToSix},
		Holidays: map[string]bool{"2027-01-26": true}}
	start := time.Date(2027, 1, 25, 10, 0, 0, 0, ist)
	got, err := cal.AddBusiness(start, 16*time.Hour)
	if err != nil {
		t.Fatal(err)
	}
	if want := time.Date(2027, 1, 27, 17, 0, 0, 0, ist); !got.Equal(want) {
		t.Fatalf("got %s, want %s", got, want)
	}
	// Starting outside hours moves to the next opening; a weekend is skipped.
	got, _ = cal.AddBusiness(time.Date(2027, 1, 29, 19, 0, 0, 0, ist), time.Hour) // Friday evening
	if want := time.Date(2027, 2, 1, 10, 0, 0, 0, ist); !got.Equal(want) {
		t.Fatalf("got %s, want %s", got, want)
	}
}

// Same cases as the feature "Daily recurrence across a daylight-saving change".
func TestDailyAtAcrossDST(t *testing.T) {
	cases := []struct {
		tz    string
		start string
	}{{"Europe/London", "2027-03-27T00:00:00Z"}, {"America/New_York", "2027-03-13T00:00:00Z"}, {"Asia/Kolkata", "2027-01-10T00:00:00Z"}}
	for _, c := range cases {
		loc := mustLoad(t, c.tz)
		from, _ := time.Parse(time.RFC3339, c.start)
		occ := DailyAt(loc, 9, 0, from, from.Add(72*time.Hour))
		if len(occ) != 3 {
			t.Fatalf("%s: %d occurrences, want 3", c.tz, len(occ))
		}
		for _, o := range occ {
			if o.In(loc).Hour() != 9 || o.In(loc).Minute() != 0 {
				t.Fatalf("%s: occurrence %s is not 09:00 local", c.tz, o.In(loc))
			}
		}
	}
	// In London the UTC instant moves from 09:00Z to 08:00Z when summer time starts (28 March 2027).
	loc := mustLoad(t, "Europe/London")
	from, _ := time.Parse(time.RFC3339, "2027-03-27T00:00:00Z")
	occ := DailyAt(loc, 9, 0, from, from.Add(72*time.Hour))
	if occ[0].UTC().Hour() != 9 || occ[1].UTC().Hour() != 8 {
		t.Fatalf("UTC hours %d, %d; want 9 then 8", occ[0].UTC().Hour(), occ[1].UTC().Hour())
	}
}
