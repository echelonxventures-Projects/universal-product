-- 0002 Control-plane registries (KERNEL-DESIGN §8, §10). Platform scope: written only through governance.
CREATE TABLE registry.snapshots (
  id            text PRIMARY KEY CHECK (id ~ '^sha256:[0-9a-f]{64}$'),
  merkle_root   text NOT NULL,
  signature     text NOT NULL,
  git_commit    text NOT NULL CHECK (git_commit ~ '^[0-9a-f]{40}$'),
  created_at    timestamptz NOT NULL DEFAULT now()
);
CREATE TABLE registry.object_types (
  id            text NOT NULL,                       -- e.g. ucos.order.Order
  version       text NOT NULL,
  universe      text NOT NULL,
  capability    text NOT NULL,
  schema        jsonb NOT NULL,
  storage       text NOT NULL CHECK (storage IN ('generated-table', 'generic-objects')),
  status        text NOT NULL CHECK (status IN ('proposed', 'published', 'deprecated')),
  snapshot_id   text REFERENCES registry.snapshots(id),
  published_at  timestamptz,
  PRIMARY KEY (id, version)
);
CREATE TABLE registry.capabilities (
  id            text NOT NULL,
  version       text NOT NULL,
  manifest      jsonb NOT NULL,
  phase         int  NOT NULL CHECK (phase BETWEEN 0 AND 7),
  maturity      text NOT NULL,
  digest        text NOT NULL CHECK (digest ~ '^sha256:[0-9a-f]{64}$'),
  snapshot_id   text REFERENCES registry.snapshots(id),
  PRIMARY KEY (id, version)
);
CREATE TABLE registry.blueprints (
  id            text PRIMARY KEY CHECK (id ~ '^ucos:blueprint:sha256:[0-9a-f]{64}$'),
  tenant        text NOT NULL,
  pd_ref        text NOT NULL,
  snapshot_id   text NOT NULL REFERENCES registry.snapshots(id),
  body          jsonb NOT NULL,
  gap_report    jsonb NOT NULL,
  status        text NOT NULL CHECK (status IN ('composed', 'certified', 'active', 'superseded', 'rolled-back')),
  certification text,
  created_at    timestamptz NOT NULL DEFAULT now()
);
GRANT SELECT ON ALL TABLES IN SCHEMA registry TO ucos_app, ucos_readonly;
