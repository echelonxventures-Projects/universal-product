// Package temporal holds the kernel's pure time logic (U13): business-time arithmetic on a calendar with
// opening hours and holidays, and wall-clock recurrences that stay at the same local time across
// daylight-saving changes. Scheduling itself happens only in the trigger engine (TMP-L4).
package temporal

import (
	"errors"
	"time"
)

// Hours is one opening window of a day, as offsets from local midnight.
type Hours struct{ Open, Close time.Duration }

// BusinessCalendar describes when business time runs (U13 Calendar + business-hours template).
type BusinessCalendar struct {
	Location *time.Location
	Week     map[time.Weekday]Hours // days missing from the map are closed
	Holidays map[string]bool        // "YYYY-MM-DD" in the calendar's location
}

// AddBusiness returns the instant at which d of business time has elapsed after start.
func (c BusinessCalendar) AddBusiness(start time.Time, d time.Duration) (time.Time, error) {
	if c.Location == nil || len(c.Week) == 0 {
		return time.Time{}, errors.New("temporal: calendar needs a location and opening hours")
	}
	if d < 0 {
		return time.Time{}, errors.New("temporal: negative business duration")
	}
	t := start.In(c.Location)
	for day := 0; day < 3660; day++ { // bounded: ten years of calendar days
		midnight := time.Date(t.Year(), t.Month(), t.Day(), 0, 0, 0, 0, c.Location)
		h, open := c.Week[t.Weekday()]
		if open && !c.Holidays[midnight.Format("2006-01-02")] {
			from, to := midnight.Add(h.Open), midnight.Add(h.Close)
			if t.Before(from) {
				t = from
			}
			if t.Before(to) {
				if avail := to.Sub(t); d <= avail {
					return t.Add(d), nil
				} else {
					d -= avail
				}
			}
		}
		t = midnight.AddDate(0, 0, 1)
	}
	return time.Time{}, errors.New("temporal: no business time within ten years")
}

// DailyAt lists occurrences of a daily recurrence at hour:minute local time in loc, within [from, to).
// The local time stays fixed across daylight-saving changes; the UTC instant moves.
func DailyAt(loc *time.Location, hour, minute int, from, to time.Time) []time.Time {
	var out []time.Time
	d := from.In(loc)
	for day := time.Date(d.Year(), d.Month(), d.Day(), 0, 0, 0, 0, loc); day.Before(to); day = day.AddDate(0, 0, 1) {
		occ := time.Date(day.Year(), day.Month(), day.Day(), hour, minute, 0, 0, loc)
		if !occ.Before(from) && occ.Before(to) {
			out = append(out, occ)
		}
	}
	return out
}
