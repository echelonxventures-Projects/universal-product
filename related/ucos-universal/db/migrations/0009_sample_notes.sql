-- 0009 Generated physical table for the Phase 0 sample pack (ADR-003; U57 Appendix S).
-- Core object types get typed tables like this one, produced by gen.ddl.postgres from the object-type schema
-- (spec/object-types/ucos.sample.Note.schema.json). Tenant extensions go to the `custom` column.
CREATE TABLE packs.sample_note (
  tenant_id     text NOT NULL,
  id            text NOT NULL CHECK (id ~ '^ucos:note:'),
  version       bigint NOT NULL DEFAULT 1 CHECK (version >= 1),
  title         jsonb NOT NULL,                        -- LocalizedText
  body          text NOT NULL DEFAULT '',
  status        text NOT NULL CHECK (status IN ('draft', 'published', 'archived')),
  author        text NOT NULL,
  remind_at     timestamptz,
  published_at  timestamptz,
  tags          text[] NOT NULL DEFAULT '{}',
  custom        jsonb NOT NULL DEFAULT '{}',
  created_at    timestamptz NOT NULL DEFAULT now(),
  PRIMARY KEY (tenant_id, id),
  CHECK (status <> 'published' OR published_at IS NOT NULL)
);
ALTER TABLE packs.sample_note ENABLE ROW LEVEL SECURITY;
ALTER TABLE packs.sample_note FORCE ROW LEVEL SECURITY;
CREATE POLICY tenant_isolation ON packs.sample_note
  USING (tenant_id = kernel.current_tenant()) WITH CHECK (tenant_id = kernel.current_tenant());
GRANT SELECT, INSERT, UPDATE ON packs.sample_note TO ucos_app;
