# Runbook — platform genesis

| Field | Value |
|---|---|
| Purpose | Create the root authority and the platform's trust anchors, once, before the first blueprint is activated (U01 bootstrap) |
| When | End of Phase 0, after the exit test passes in the sandbox cell |
| Output | A signed `GenesisRecord` (`spec/genesis/genesis-record.schema.json`; an annotated example sits next to it) |
| Owner | Architecture Board chair (Bipin Kumar) |
| Decision | ADR-034 (board composition), ADR-036 (CI) |

## Preconditions
1. **Board seated.** At least three members (chair, chief architect, CISO) are named, each with a FIDO2 hardware key registered at AAL3. *Today only the chair is named, so genesis cannot run yet.*
2. **Release candidate.** A tagged commit (`vX.Y.Z`) whose CI run is green, including the self-test and the Phase 0 exit scenarios.
3. **Cell ready.** The first cell is provisioned from `deploy/` and passes its smoke test.
4. **KMS or HSM** available in the cell's region, with key-creation rights limited to the CISO.

## Ceremony
Run it on a video call that is recorded, with at least one witness who is not a board member. Every step is logged in the ceremony log.

1. **Verify the release.** Each member independently checks out the tag and runs `tools/ci.sh`. Everyone must get `CI PASSED` at the same commit.
2. **Create the trust anchors** in the KMS (non-exportable, asymmetric):
   - the registry snapshot signing key;
   - the audit anchoring key (daily Merkle roots);
   - the certification attestation key (DSSE);
   - the context-envelope signing key.

   Record each key id and the sha256 fingerprint of its public key.
3. **Build the registry snapshot** from the tag and sign it with the snapshot key. Record its digest. Also record the digests of `spec/certification/gates.yaml` and of `spec/policies/platform-baseline.cedar`.
4. **Fill in the GenesisRecord.** Include the release, the root authority (level 5, members, quorum 2 of 3), the trust anchors, the adopted definitions (master version, snapshot, digests, accepted ADRs) and the witnesses. Validate it against the schema.
5. **Sign.** At least two members, including the chair or the CISO, sign the canonical JSON (JCS) with their hardware keys.
6. **Store** the record in the audit store as the first record of the platform chain, and copy it to write-once storage.
7. **Activate the control plane** with the snapshot, then run the audit chain verification and the snapshot signature verification. Both must pass.
8. **Record the first DecisionRecords:** adopt master vX.Y, the gate catalogue, the baseline policies, and the sandbox activation of the `sample-p0` blueprint.

## Rollback
If any step fails before step 6, destroy the keys created in step 2 and start again. After step 6 the record is immutable. A correction is a new DecisionRecord made by the board, never an edit.

## Afterwards
- Key rotation follows U65 key policies. The genesis record keeps its original key ids; rotations are new DecisionRecords that reference it.
- A member who leaves the board is removed by a level-5 decision with quorum, and their hardware key is revoked the same day.
