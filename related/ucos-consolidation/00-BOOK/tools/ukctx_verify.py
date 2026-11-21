#!/usr/bin/env python3
"""
UCOS Ω∞ — Independent verification of the context projections (UCOS-UCTX-001, MB7).

THIS FILE HOLDS NO VERIFICATION LOGIC. It is the reference ADOPTER of the Universal
Formal Independence framework in 00-BOOK/tools/ufi.py, and it exists at this path
because verify.sh, the CI workflow, the UEC governed enforcement inventory and the
generated-artifact registry all name it — an entry point that moved would be a
protection that quietly stopped being invoked.

WHY IT IS A SHIM RATHER THAN A VERIFIER. MB7 is "a producer validated only by its own
programme". The first closure of it, for this capability, was a purpose-built verifier.
Written 33 times that becomes 33 new things that can each be uniformly wrong, which is
the defect again with more files. So the checks were extracted into ONE implementation
that every producer can adopt, and what remains here is the adoption: a declaration
naming this capability's own authorities and its own manifest.

The framework shares CODE. It never shares AUTHORITY: the three things this adopter
declares — its authorities, its surfaces, its manifest — are its own, and ufi.py holds
no list of any of them.

What is verified, and the evidence that it verifies anything, is documented in
00-BOOK/tools/ufi.py and measured by the non-vacuity probes in
.github/workflows/uctx-gate.yml.

Usage:
    python3 00-BOOK/tools/ukctx_verify.py            # verify; exit 1 on any finding
    python3 00-BOOK/tools/ukctx_verify.py --report   # list findings and exit 0

Standard library only. Reads. Writes nothing.
"""

from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import ufi  # noqa: E402

#: This capability's adoption of the framework. Everything specific to UCOS-UCTX-001 —
#: which instruments are its authorities, which files are its surfaces, where its
#: reviewed templates live — is declared there and nowhere in this file.
DECLARATION = os.path.join(ufi.REPO, "00-BOOK", "DATA", "independence", "uctx.json")


def main(argv=None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    return ufi.verify(DECLARATION, ufi.REPO, report_only="--report" in argv)


if __name__ == "__main__":
    sys.exit(main())
