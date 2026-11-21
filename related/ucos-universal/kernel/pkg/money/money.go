// Package money implements exact Money arithmetic (U14 CUR laws): integer minor units, no floating point,
// and allocation that always conserves the total (gate ARCH-CUR-02).
package money

import (
	"errors"
	"fmt"
	"math/big"
	"sort"
	"strings"
)

// MinorUnits for the currencies UCOS launches with; must match spec/seed/refdata/iso4217.yaml (tested).
var MinorUnits = map[string]int{
	"INR": 2, "AED": 2, "USD": 2, "EUR": 2, "GBP": 2, "SAR": 2, "JPY": 0, "KWD": 3, "BHD": 3, "OMR": 3,
}

// Money is an amount in integer minor units of a currency.
type Money struct {
	Minor    int64
	Currency string
}

var (
	ErrCurrency = errors.New("money: unknown currency")
	ErrMismatch = errors.New("money: currency mismatch")
	ErrFormat   = errors.New("money: invalid amount")
)

// Parse reads a decimal string ("1598.00") in currency cur. More decimals than the currency allows is an error.
func Parse(amount, cur string) (Money, error) {
	scale, ok := MinorUnits[cur]
	if !ok {
		return Money{}, fmt.Errorf("%w: %s", ErrCurrency, cur)
	}
	neg := strings.HasPrefix(amount, "-")
	a := strings.TrimPrefix(amount, "-")
	whole, frac, _ := strings.Cut(a, ".")
	if whole == "" || len(frac) > scale || strings.ContainsAny(whole+frac, "+- ") {
		return Money{}, fmt.Errorf("%w: %q for %s", ErrFormat, amount, cur)
	}
	frac += strings.Repeat("0", scale-len(frac))
	n, ok := new(big.Int).SetString(whole+frac, 10)
	if !ok || !n.IsInt64() {
		return Money{}, fmt.Errorf("%w: %q", ErrFormat, amount)
	}
	v := n.Int64()
	if neg {
		v = -v
	}
	return Money{Minor: v, Currency: cur}, nil
}

// String formats with exactly the currency's minor units: "1598.00".
func (m Money) String() string {
	scale := MinorUnits[m.Currency]
	sign, v := "", m.Minor
	if v < 0 {
		sign, v = "-", -v
	}
	s := fmt.Sprintf("%0*d", scale+1, v)
	if scale == 0 {
		return sign + s
	}
	return sign + s[:len(s)-scale] + "." + s[len(s)-scale:]
}

// Add returns m + o; both must be in the same currency.
func (m Money) Add(o Money) (Money, error) {
	if m.Currency != o.Currency {
		return Money{}, ErrMismatch
	}
	return Money{Minor: m.Minor + o.Minor, Currency: m.Currency}, nil
}

// Allocate splits total in proportion to weights using the largest-remainder method.
// The shares always sum to total exactly; each share differs from its exact proportion by less than one
// minor unit; ties go to the earlier weight, so the result is deterministic.
func Allocate(total Money, weights []int64) ([]Money, error) {
	if len(weights) == 0 {
		return nil, errors.New("money: no weights")
	}
	sum := new(big.Int)
	for _, w := range weights {
		if w < 0 {
			return nil, errors.New("money: negative weight")
		}
		sum.Add(sum, big.NewInt(w))
	}
	if sum.Sign() == 0 {
		return nil, errors.New("money: weights sum to zero")
	}
	neg := total.Minor < 0
	t := big.NewInt(total.Minor)
	if neg {
		t.Neg(t)
	}
	type part struct {
		i   int
		rem *big.Int
	}
	shares := make([]int64, len(weights))
	parts := make([]part, len(weights))
	allocated := new(big.Int)
	for i, w := range weights {
		num := new(big.Int).Mul(t, big.NewInt(w))
		q, r := new(big.Int).QuoRem(num, sum, new(big.Int))
		shares[i] = q.Int64()
		allocated.Add(allocated, q)
		parts[i] = part{i, r}
	}
	left := new(big.Int).Sub(t, allocated).Int64()
	sort.SliceStable(parts, func(a, b int) bool { return parts[a].rem.Cmp(parts[b].rem) > 0 })
	for k := int64(0); k < left; k++ {
		shares[parts[k].i]++
	}
	out := make([]Money, len(weights))
	for i, s := range shares {
		if neg {
			s = -s
		}
		out[i] = Money{Minor: s, Currency: total.Currency}
	}
	return out, nil
}
