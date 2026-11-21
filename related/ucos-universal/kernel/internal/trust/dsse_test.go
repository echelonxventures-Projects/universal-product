package trust

import (
	"crypto/ed25519"
	"testing"
)

func TestSignVerify(t *testing.T) {
	s, err := NewSigner(make([]byte, 32))
	if err != nil {
		t.Fatal(err)
	}
	env := s.Sign(InTotoType, []byte(`{"hello":"world"}`))
	if p, err := Verify(env, s.Public()); err != nil || string(p) != `{"hello":"world"}` {
		t.Fatalf("verify: %v %s", err, p)
	}
	env.PayloadType = "text/plain" // type is bound by PAE
	if _, err := Verify(env, s.Public()); err == nil {
		t.Fatal("changed payload type accepted")
	}
	other, _ := NewSigner(append(make([]byte, 31), 1))
	if _, err := Verify(s.Sign(InTotoType, []byte("x")), other.Public()); err == nil {
		t.Fatal("wrong key accepted")
	}
	if string(PAE("t", []byte("ab"))) != "DSSEv1 1 t 2 ab" {
		t.Fatal("PAE format")
	}
	_ = ed25519.PublicKeySize
}
