-- 0004 Generic bitemporal object store for registry-only and low-volume types (ADR-003, ADR-011).
-- Current state lives in kernel.objects; every version is kept in kernel.object_versions.
CREATE TABLE kernel.objects (
  tenant_id     text NOT NULL,
  type          text NOT NULL,
  id            text NOT NULL CHECK (id ~ '^ucos:[a-z][a-z0-9-]{0,31}:'),
  version       bigint NOT NULL CHECK (version >= 1),
  status        text,
  attributes    jsonb NOT NULL DEFAULT '{}',
  custom        jsonb NOT NULL DEFAULT '{}',           -- tenant extension fields
  valid         tstzrange NOT NULL DEFAULT tstzrange(now(), NULL),
  created_at    timestamptz NOT NULL DEFAULT now(),
  updated_at    timestamptz NOT NULL DEFAULT now(),
  PRIMARY KEY (tenant_id, type, id)
);
CREATE INDEX objects_attributes_gin ON kernel.objects USING gin (attributes jsonb_path_ops);

CREATE TABLE kernel.object_versions (
  tenant_id     text NOT NULL,
  type          text NOT NULL,
  id            text NOT NULL,
  version       bigint NOT NULL,
  attributes    jsonb NOT NULL,
  custom        jsonb NOT NULL,
  valid         tstzrange NOT NULL,                    -- valid time (business)
  recorded      tstzrange NOT NULL DEFAULT tstzrange(now(), NULL),  -- transaction time
  PRIMARY KEY (tenant_id, type, id, version)
);

ALTER TABLE kernel.objects ENABLE ROW LEVEL SECURITY;
ALTER TABLE kernel.objects FORCE ROW LEVEL SECURITY;
ALTER TABLE kernel.object_versions ENABLE ROW LEVEL SECURITY;
ALTER TABLE kernel.object_versions FORCE ROW LEVEL SECURITY;
CREATE POLICY tenant_isolation ON kernel.objects
  USING (tenant_id = kernel.current_tenant()) WITH CHECK (tenant_id = kernel.current_tenant());
CREATE POLICY tenant_isolation ON kernel.object_versions
  USING (tenant_id = kernel.current_tenant()) WITH CHECK (tenant_id = kernel.current_tenant());

-- Every write to an object appends a version (history is never rewritten).
CREATE OR REPLACE FUNCTION kernel.record_version() RETURNS trigger LANGUAGE plpgsql AS $$
BEGIN
  IF TG_OP = 'UPDATE' THEN
    IF NEW.version <> OLD.version + 1 THEN
      RAISE EXCEPTION 'version must increase by one (expected %, got %)', OLD.version + 1, NEW.version
        USING ERRCODE = '40001';
    END IF;
    UPDATE kernel.object_versions SET recorded = tstzrange(lower(recorded), now())
     WHERE tenant_id = OLD.tenant_id AND type = OLD.type AND id = OLD.id AND version = OLD.version;
  END IF;
  INSERT INTO kernel.object_versions (tenant_id, type, id, version, attributes, custom, valid)
  VALUES (NEW.tenant_id, NEW.type, NEW.id, NEW.version, NEW.attributes, NEW.custom, NEW.valid);
  NEW.updated_at := now();
  RETURN NEW;
END $$;
CREATE TRIGGER objects_versioning BEFORE INSERT OR UPDATE ON kernel.objects
  FOR EACH ROW EXECUTE FUNCTION kernel.record_version();

GRANT SELECT, INSERT, UPDATE ON kernel.objects TO ucos_app;
GRANT SELECT, INSERT, UPDATE ON kernel.object_versions TO ucos_app;
GRANT SELECT ON kernel.objects, kernel.object_versions TO ucos_readonly;
