// Package trust signs and verifies with the platform's trust anchors (genesis record, U01/U65): Ed25519 keys and
// DSSE envelopes (https://github.com/secure-systems-lab/dsse) over in-toto statements.
package trust

import (
	"crypto/ed25519"
	"crypto/sha256"
	"encoding/base64"
	"encoding/hex"
	"encoding/json"
	"errors"
	"fmt"
	"strconv"
)

// Signer holds one Ed25519 key. KeyID is the sha256 of the public key, as recorded in the genesis record.
type Signer struct {
	priv  ed25519.PrivateKey
	KeyID string
}

// NewSigner builds a signer from a 32-byte seed (in production the key lives in the KMS/HSM; see genesis runbook).
func NewSigner(seed []byte) (*Signer, error) {
	if len(seed) != ed25519.SeedSize {
		return nil, fmt.Errorf("trust: seed must be %d bytes", ed25519.SeedSize)
	}
	priv := ed25519.NewKeyFromSeed(seed)
	return &Signer{priv: priv, KeyID: KeyID(priv.Public().(ed25519.PublicKey))}, nil
}

func (s *Signer) Public() ed25519.PublicKey { return s.priv.Public().(ed25519.PublicKey) }

func KeyID(pub ed25519.PublicKey) string {
	sum := sha256.Sum256(pub)
	return "sha256:" + hex.EncodeToString(sum[:])
}

// PAE is DSSE's pre-authentication encoding.
func PAE(payloadType string, payload []byte) []byte {
	return []byte("DSSEv1 " + strconv.Itoa(len(payloadType)) + " " + payloadType + " " + strconv.Itoa(len(payload)) + " " + string(payload))
}

type Signature struct {
	KeyID string `json:"keyid"`
	Sig   string `json:"sig"`
}

type Envelope struct {
	PayloadType string      `json:"payloadType"`
	Payload     string      `json:"payload"`
	Signatures  []Signature `json:"signatures"`
}

const InTotoType = "application/vnd.in-toto+json"

func (s *Signer) Sign(payloadType string, payload []byte) Envelope {
	sig := ed25519.Sign(s.priv, PAE(payloadType, payload))
	return Envelope{PayloadType: payloadType, Payload: base64.StdEncoding.EncodeToString(payload),
		Signatures: []Signature{{KeyID: s.KeyID, Sig: base64.StdEncoding.EncodeToString(sig)}}}
}

var ErrSignature = errors.New("trust: signature does not verify")

// Verify checks that env is signed by pub and returns the payload.
func Verify(env Envelope, pub ed25519.PublicKey) ([]byte, error) {
	payload, err := base64.StdEncoding.DecodeString(env.Payload)
	if err != nil {
		return nil, ErrSignature
	}
	want := KeyID(pub)
	for _, s := range env.Signatures {
		if s.KeyID != want {
			continue
		}
		sig, err := base64.StdEncoding.DecodeString(s.Sig)
		if err == nil && ed25519.Verify(pub, PAE(env.PayloadType, payload), sig) {
			return payload, nil
		}
	}
	return nil, ErrSignature
}

// Statement is an in-toto v1 statement.
type Statement struct {
	Type          string          `json:"_type"`
	Subject       []Subject       `json:"subject"`
	PredicateType string          `json:"predicateType"`
	Predicate     json.RawMessage `json:"predicate"`
}

type Subject struct {
	Name   string            `json:"name"`
	Digest map[string]string `json:"digest"`
}
