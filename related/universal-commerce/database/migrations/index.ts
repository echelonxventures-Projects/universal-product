export interface Migration {
  name: string;
  up: (conn: any) => Promise<void>;
  down: (conn: any) => Promise<void>;
}

export const migrations: Migration[] = [
  {
    name: '001-create-tenants',
    up: async (db) => {
      await db.execute(`
        CREATE TABLE IF NOT EXISTS tenants (
          id VARCHAR PRIMARY KEY,
          name VARCHAR NOT NULL,
          status VARCHAR DEFAULT 'active',
          created_at TIMESTAMP DEFAULT NOW()
        )
      `);
    },
    down: async (db) => {
      await db.execute('DROP TABLE IF EXISTS tenants');
    }
  },
  {
    name: '002-create-products',
    up: async (db) => {
      await db.execute(`
        CREATE TABLE IF NOT EXISTS products (
          id VARCHAR PRIMARY KEY,
          sku VARCHAR UNIQUE NOT NULL,
          name VARCHAR NOT NULL,
          description TEXT,
          category_ids TEXT[],
          attributes JSONB,
          variants JSONB,
          status VARCHAR DEFAULT 'draft',
          tenant_id VARCHAR NOT NULL,
          created_at TIMESTAMP DEFAULT NOW(),
          updated_at TIMESTAMP DEFAULT NOW(),
          FOREIGN KEY (tenant_id) REFERENCES tenants(id)
        )
      `);
      await db.execute('CREATE INDEX IF NOT EXISTS idx_products_tenant ON products(tenant_id)');
      await db.execute('CREATE INDEX IF NOT EXISTS idx_products_sku ON products(sku)');
    },
    down: async (db) => {
      await db.execute('DROP TABLE IF EXISTS products');
    }
  },
  {
    name: '003-create-offers',
    up: async (db) => {
      await db.execute(`
        CREATE TABLE IF NOT EXISTS offers (
          id VARCHAR PRIMARY KEY,
          code VARCHAR UNIQUE NOT NULL,
          name VARCHAR NOT NULL,
          description TEXT,
          type VARCHAR NOT NULL,
          value NUMERIC,
          currency VARCHAR DEFAULT 'USD',
          eligibility JSONB,
          conditions JSONB,
          schedule JSONB,
          usage JSONB DEFAULT '{}',
          status VARCHAR DEFAULT 'draft',
          tenant_id VARCHAR NOT NULL,
          created_at TIMESTAMP DEFAULT NOW(),
          FOREIGN KEY (tenant_id) REFERENCES tenants(id)
        )
      `);
    },
    down: async (db) => {
      await db.execute('DROP TABLE IF EXISTS offers');
    }
  },
  {
    name: '004-create-orders',
    up: async (db) => {
      await db.execute(`
        CREATE TABLE IF NOT EXISTS orders (
          id VARCHAR PRIMARY KEY,
          order_number VARCHAR UNIQUE NOT NULL,
          customer_id VARCHAR NOT NULL,
          status VARCHAR DEFAULT 'pending',
          items JSONB,
          subtotal NUMERIC DEFAULT 0,
          tax NUMERIC DEFAULT 0,
          discount NUMERIC DEFAULT 0,
          total NUMERIC DEFAULT 0,
          shipping_address JSONB,
          billing_address JSONB,
          payment_id VARCHAR,
          fulfillment_id VARCHAR,
          tenant_id VARCHAR NOT NULL,
          created_at TIMESTAMP DEFAULT NOW(),
          updated_at TIMESTAMP DEFAULT NOW()
        )
      `);
      await db.execute('CREATE INDEX IF NOT EXISTS idx_orders_tenant ON orders(tenant_id)');
      await db.execute('CREATE INDEX IF NOT EXISTS idx_orders_status ON orders(status)');
    },
    down: async (db) => {
      await db.execute('DROP TABLE IF EXISTS orders');
    }
  }
];

export async function migrateUp(db: any): Promise<void> {
  for (const migration of migrations) {
    console.log(`Migrating: ${migration.name}`);
    await migration.up(db);
  }
}

export async function migrateDown(db: any): Promise<void> {
  for (const migration of [...migrations].reverse()) {
    console.log(`Rolling back: ${migration.name}`);
    await migration.down(db);
  }
}
