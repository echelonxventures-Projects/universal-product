-- 0003 Tenants and their placement (U10, U73). Platform scope.
CREATE TABLE registry.tenants (
  id            text PRIMARY KEY,                    -- ucos:tenant:...
  slug          text NOT NULL UNIQUE CHECK (slug ~ '^[a-z][a-z0-9-]{1,62}$'),
  cell          text NOT NULL,
  residency     text[] NOT NULL DEFAULT '{}',
  status        text NOT NULL CHECK (status IN ('provisioning', 'active', 'suspended', 'closed')),
  active_blueprint text REFERENCES registry.blueprints(id),
  created_at    timestamptz NOT NULL DEFAULT now()
);
GRANT SELECT ON registry.tenants TO ucos_app, ucos_readonly;
