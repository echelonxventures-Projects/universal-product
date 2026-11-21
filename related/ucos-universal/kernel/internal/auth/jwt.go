// Package auth verifies OIDC access tokens (RS256) against the issuer's JWKS and maps them to a ContextEnvelope
// (U09, U16). Only allow-listed issuers are trusted; each issuer belongs to exactly one tenant, so a token for one
// tenant can never act in another (K-S2).
package auth

import (
	"context"
	"crypto"
	"crypto/rsa"
	"crypto/sha256"
	"encoding/base64"
	"encoding/json"
	"errors"
	"fmt"
	"math/big"
	"net/http"
	"regexp"
	"sort"
	"strconv"
	"strings"
	"sync"
	"time"

	"ucos.io/kernel/pkg/ctxenv"
)

// TenantConfig is what the resolver needs to know about a tenant's issuer and defaults.
type TenantConfig struct {
	Issuer       string   `json:"issuer"`  // exact "iss" value
	JWKSURL      string   `json:"jwksUrl"` // where the issuer publishes keys
	Tenant       string   `json:"tenant"`  // ucos:tenant:...
	Locale       string   `json:"locale"`
	Currency     string   `json:"currency"`
	TZ           string   `json:"tz"`
	Reality      string   `json:"reality"`      // physical | simulated | hypothetical
	Jurisdiction string   `json:"jurisdiction"` // ucos:jur:XX for the actor role
	Locales      []string `json:"locales"`      // enabled locales for Accept-Language negotiation (default: Locale only)
}

type Verifier struct {
	tenants map[string]TenantConfig // by issuer
	client  *http.Client
	clock   func() time.Time
	mu      sync.Mutex
	keys    map[string]map[string]*rsa.PublicKey // issuer -> kid -> key
	fetched map[string]time.Time
}

var (
	ErrToken  = errors.New("auth: invalid token")
	ErrIssuer = errors.New("auth: issuer not trusted")
)

func NewVerifier(tenants []TenantConfig, client *http.Client, clock func() time.Time) *Verifier {
	v := &Verifier{tenants: map[string]TenantConfig{}, client: client, clock: clock,
		keys: map[string]map[string]*rsa.PublicKey{}, fetched: map[string]time.Time{}}
	if v.client == nil {
		v.client = &http.Client{Timeout: 5 * time.Second}
	}
	if v.clock == nil {
		v.clock = time.Now
	}
	for _, t := range tenants {
		v.tenants[t.Issuer] = t
	}
	return v
}

type Claims struct {
	Iss         string `json:"iss"`
	Sub         string `json:"sub"`
	Exp         int64  `json:"exp"`
	Nbf         int64  `json:"nbf"`
	Iat         int64  `json:"iat"`
	Azp         string `json:"azp"`
	Acr         string `json:"acr"`
	RealmAccess struct {
		Roles []string `json:"roles"`
	} `json:"realm_access"`
	Locale            string `json:"locale"`
	PreferredUsername string `json:"preferred_username"`
	// Act is the RFC 8693 actor claim: the token's subject is represented by another party (an agent).
	Act *struct {
		Sub string `json:"sub"`
	} `json:"act"`
}

func b64(s string) ([]byte, error) {
	return base64.RawURLEncoding.DecodeString(strings.TrimRight(s, "="))
}

// Verify checks signature, issuer and time claims and returns the claims and the issuer's tenant config.
func (v *Verifier) Verify(ctx context.Context, token string) (*Claims, TenantConfig, error) {
	parts := strings.Split(token, ".")
	if len(parts) != 3 {
		return nil, TenantConfig{}, ErrToken
	}
	hb, err1 := b64(parts[0])
	pb, err2 := b64(parts[1])
	sig, err3 := b64(parts[2])
	if err1 != nil || err2 != nil || err3 != nil {
		return nil, TenantConfig{}, ErrToken
	}
	var hdr struct{ Alg, Kid, Typ string }
	var c Claims
	if json.Unmarshal(hb, &hdr) != nil || json.Unmarshal(pb, &c) != nil {
		return nil, TenantConfig{}, ErrToken
	}
	if hdr.Alg != "RS256" { // no "none", no algorithm confusion
		return nil, TenantConfig{}, fmt.Errorf("%w: algorithm %q not accepted", ErrToken, hdr.Alg)
	}
	tc, ok := v.tenants[c.Iss]
	if !ok {
		return nil, TenantConfig{}, ErrIssuer
	}
	key, err := v.key(ctx, tc, hdr.Kid)
	if err != nil {
		return nil, TenantConfig{}, err
	}
	digest := sha256.Sum256([]byte(parts[0] + "." + parts[1]))
	if err := rsa.VerifyPKCS1v15(key, crypto.SHA256, digest[:], sig); err != nil {
		return nil, TenantConfig{}, fmt.Errorf("%w: bad signature", ErrToken)
	}
	now := v.clock().Unix()
	const skew = 30
	if c.Exp == 0 || now > c.Exp+skew || (c.Nbf != 0 && now+skew < c.Nbf) {
		return nil, TenantConfig{}, fmt.Errorf("%w: expired or not yet valid", ErrToken)
	}
	if c.Sub == "" {
		return nil, TenantConfig{}, fmt.Errorf("%w: no subject", ErrToken)
	}
	return &c, tc, nil
}

func (v *Verifier) key(ctx context.Context, tc TenantConfig, kid string) (*rsa.PublicKey, error) {
	v.mu.Lock()
	k := v.keys[tc.Issuer][kid]
	last := v.fetched[tc.Issuer]
	v.mu.Unlock()
	if k != nil {
		return k, nil
	}
	if v.clock().Sub(last) < 10*time.Second { // unknown kid: refetch at most every 10 s
		return nil, fmt.Errorf("%w: unknown key id", ErrToken)
	}
	req, _ := http.NewRequestWithContext(ctx, http.MethodGet, tc.JWKSURL, nil)
	resp, err := v.client.Do(req)
	if err != nil {
		return nil, fmt.Errorf("auth: fetching keys: %w", err)
	}
	defer resp.Body.Close()
	var set struct {
		Keys []struct{ Kty, Kid, Use, Alg, N, E string } `json:"keys"`
	}
	if err := json.NewDecoder(resp.Body).Decode(&set); err != nil {
		return nil, fmt.Errorf("auth: decoding keys: %w", err)
	}
	keys := map[string]*rsa.PublicKey{}
	for _, j := range set.Keys {
		if j.Kty != "RSA" || (j.Use != "" && j.Use != "sig") {
			continue
		}
		nb, err1 := b64(j.N)
		eb, err2 := b64(j.E)
		if err1 != nil || err2 != nil {
			continue
		}
		keys[j.Kid] = &rsa.PublicKey{N: new(big.Int).SetBytes(nb), E: int(new(big.Int).SetBytes(eb).Int64())}
	}
	v.mu.Lock()
	v.keys[tc.Issuer], v.fetched[tc.Issuer] = keys, v.clock()
	v.mu.Unlock()
	if k := keys[kid]; k != nil {
		return k, nil
	}
	return nil, fmt.Errorf("%w: unknown key id", ErrToken)
}

// Envelope builds the context envelope for a verified token (U16 resolver, Phase 0 subset).
func Envelope(c *Claims, tc TenantConfig, channel string, now time.Time) *ctxenv.Envelope {
	locale := tc.Locale
	if c.Locale != "" {
		locale = c.Locale
	}
	reality := tc.Reality
	if reality == "" {
		reality = "physical"
	}
	sideEffects := "full"
	if reality != "physical" {
		sideEffects = "none"
	}
	jur := map[string][]string{}
	if tc.Jurisdiction != "" {
		jur["actor"] = []string{tc.Jurisdiction}
	}
	actor := ctxenv.Actor{Identity: "ucos:identity:" + c.Sub, Kind: "human"}
	switch {
	case c.Act != nil && c.Act.Sub != "":
		actor = ctxenv.Actor{Identity: "ucos:agent:" + c.Act.Sub, Kind: "agent", OnBehalfOf: "ucos:identity:" + c.Sub}
	case strings.HasPrefix(c.PreferredUsername, "service-account-") && c.Azp != "":
		actor = ctxenv.Actor{Identity: "ucos:service:" + c.Azp, Kind: "service"}
	}
	return &ctxenv.Envelope{
		V: 1, Tenant: tc.Tenant, Actor: actor,
		Roles: c.RealmAccess.Roles, Jurisdiction: jur, Locale: locale, Currency: tc.Currency, TZ: tc.TZ,
		Time: ctxenv.Time{Now: now}, Frame: ctxenv.Frame{Reality: reality, SideEffectPolicy: sideEffects},
		Channel: channel, Risk: ctxenv.Risk{Band: "unknown"}, Simulation: reality != "physical", Exp: c.Exp,
	}
}

var purposeRe = regexp.MustCompile(`^[a-z][a-z0-9-]{1,62}$`)

// Narrow applies request-level context to an envelope built from the token (CTX-L2: request headers may only
// choose among what the tenant allows, never widen): Accept-Language picks one of the tenant's enabled locales,
// and UCOS-Purpose declares the processing purpose that purpose-bound policies check.
func Narrow(env *ctxenv.Envelope, tc TenantConfig, h http.Header) error {
	if al := h.Get("Accept-Language"); al != "" {
		if l := negotiate(al, append([]string{tc.Locale}, tc.Locales...)); l != "" {
			env.Locale = l
		}
	}
	if p := h.Get("UCOS-Purpose"); p != "" {
		if !purposeRe.MatchString(p) {
			return fmt.Errorf("UCOS-Purpose must match %s", purposeRe)
		}
		env.Purpose = p
	}
	return nil
}

// negotiate returns the enabled locale that best matches an Accept-Language header (RFC 9110 §12.5.4):
// highest q first, exact tag before primary-language match; "" when nothing matches.
func negotiate(header string, enabled []string) string {
	type pref struct {
		tag string
		q   float64
		i   int
	}
	var prefs []pref
	for i, part := range strings.Split(header, ",") {
		fields := strings.Split(strings.TrimSpace(part), ";")
		tag, q := strings.TrimSpace(fields[0]), 1.0
		for _, f := range fields[1:] {
			if v, ok := strings.CutPrefix(strings.TrimSpace(f), "q="); ok {
				if x, err := strconv.ParseFloat(v, 64); err == nil {
					q = x
				}
			}
		}
		if tag != "" && tag != "*" && q > 0 {
			prefs = append(prefs, pref{tag, q, i})
		}
	}
	sort.SliceStable(prefs, func(a, b int) bool { return prefs[a].q > prefs[b].q })
	for _, p := range prefs {
		for _, e := range enabled {
			if strings.EqualFold(p.tag, e) {
				return e
			}
		}
		primary := strings.SplitN(p.tag, "-", 2)[0]
		for _, e := range enabled {
			if strings.EqualFold(strings.SplitN(e, "-", 2)[0], primary) {
				return e
			}
		}
	}
	return ""
}
