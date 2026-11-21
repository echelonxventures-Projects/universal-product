// Package ugid creates and validates UCOS global identifiers: "ucos:<kind>:<ULID>" (spec/meta/value-types.schema.json).
package ugid

import (
	"crypto/rand"
	"errors"
	"fmt"
	"regexp"
	"time"
)

const crockford = "0123456789ABCDEFGHJKMNPQRSTVWXYZ"

var (
	kindRe = regexp.MustCompile(`^[a-z][a-z0-9-]{0,31}$`)
	// Same pattern as the UGID value type in the spec (ULID form or a hierarchical name).
	ugidRe = regexp.MustCompile(`^ucos:[a-z][a-z0-9-]{0,31}:([0-9A-HJKMNP-TV-Z]{26}|[A-Za-z0-9._~-]+(/[A-Za-z0-9._~-]+)*)$`)
)

// ErrInvalid is returned for strings that are not UGIDs.
var ErrInvalid = errors.New("ugid: invalid identifier")

// New returns a ULID-based UGID for kind at time t. The first 10 characters sort by time.
func New(kind string, t time.Time) (string, error) {
	if !kindRe.MatchString(kind) {
		return "", fmt.Errorf("ugid: invalid kind %q", kind)
	}
	var entropy [10]byte
	if _, err := rand.Read(entropy[:]); err != nil {
		return "", fmt.Errorf("ugid: entropy: %w", err)
	}
	return "ucos:" + kind + ":" + encode(uint64(t.UnixMilli()), entropy), nil
}

func encode(ms uint64, entropy [10]byte) string {
	out := make([]byte, 26)
	for i := 9; i >= 0; i-- { // 48-bit time in 10 base-32 characters
		out[i] = crockford[ms&31]
		ms >>= 5
	}
	// 80 bits of entropy in 16 characters, 5 bits at a time.
	var acc uint64
	bits, pos := 0, 10
	for _, b := range entropy {
		acc = acc<<8 | uint64(b)
		bits += 8
		for bits >= 5 {
			bits -= 5
			out[pos] = crockford[(acc>>uint(bits))&31]
			pos++
		}
	}
	return string(out)
}

// Valid reports whether s is a well-formed UGID.
func Valid(s string) bool { return ugidRe.MatchString(s) }

// Kind returns the kind segment of a valid UGID.
func Kind(s string) (string, error) {
	if !Valid(s) {
		return "", ErrInvalid
	}
	rest := s[len("ucos:"):]
	for i := 0; i < len(rest); i++ {
		if rest[i] == ':' {
			return rest[:i], nil
		}
	}
	return "", ErrInvalid
}
