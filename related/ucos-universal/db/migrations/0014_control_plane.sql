-- 0014 Control plane records for compose -> certify -> activate (U01, U58, U73, U74).
DO $$ BEGIN
  IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'ucos_control') THEN
    CREATE ROLE ucos_control NOLOGIN NOBYPASSRLS; END IF;
END $$;

-- U01: who decided what. Activation needs an approving record whose approvers exclude the requester (SoD).
CREATE TABLE registry.decision_records (
  id            text PRIMARY KEY,
  authority     text NOT NULL,
  subject       text NOT NULL,                          -- e.g. a blueprint id
  decision      text NOT NULL CHECK (decision IN ('approve-activation', 'reject-activation')),
  requested_by  text NOT NULL,
  approved_by   text[] NOT NULL CHECK (cardinality(approved_by) >= 1),
  rationale     text NOT NULL DEFAULT '',
  created_at    timestamptz NOT NULL DEFAULT now(),
  CHECK (NOT (requested_by = ANY (approved_by)))
);

-- U74: certification runs with their signed attestation (DSSE envelope over an in-toto statement).
CREATE TABLE registry.certifications (
  id            text PRIMARY KEY,
  subject       text NOT NULL,                          -- blueprint id
  snapshot_id   text NOT NULL REFERENCES registry.snapshots(id),
  profile       text NOT NULL,
  results       jsonb NOT NULL,
  passed        boolean NOT NULL,
  attestation   jsonb NOT NULL,
  valid_until   timestamptz NOT NULL,
  created_at    timestamptz NOT NULL DEFAULT now()
);

-- U73: activations and their phases.
CREATE TABLE registry.activations (
  id               bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  tenant           text NOT NULL REFERENCES registry.tenants(id),
  blueprint        text NOT NULL REFERENCES registry.blueprints(id),
  decision_record  text NOT NULL REFERENCES registry.decision_records(id),
  certification    text NOT NULL REFERENCES registry.certifications(id),
  previous         text REFERENCES registry.blueprints(id),
  phase            text NOT NULL CHECK (phase IN ('DEPLOYING', 'MIGRATING_EXPAND', 'ROUTED', 'HOLDING', 'COMPLETE', 'ROLLED_BACK', 'FAILED')),
  created_at       timestamptz NOT NULL DEFAULT now(),
  updated_at       timestamptz NOT NULL DEFAULT now()
);

GRANT USAGE ON SCHEMA registry TO ucos_control;
GRANT SELECT, INSERT, UPDATE ON ALL TABLES IN SCHEMA registry TO ucos_control;
GRANT SELECT ON registry.decision_records, registry.certifications, registry.activations TO ucos_app, ucos_readonly;
GRANT USAGE ON ALL SEQUENCES IN SCHEMA registry TO ucos_control;
