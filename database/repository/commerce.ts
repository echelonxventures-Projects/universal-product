import { Product } from '../../domains/types/commerce';

export interface DbConnection {
  query<T>(sql: string, params?: any[]): Promise<T[]>;
  execute(sql: string, params?: any[]): Promise<void>;
  transaction<T>(fn: (conn: DbConnection) => Promise<T>): Promise<T>;
  close(): Promise<void>;
}

export interface BaseRepository<T, ID> {
  findById(id: ID): Promise<T | null>;
  findAll(): Promise<T[]>;
  create(entity: Omit<T, 'id' | 'createdAt'>): Promise<T>;
  update(id: ID, entity: Partial<T>): Promise<T | null>;
  delete(id: ID): Promise<boolean>;
}

export class PostgresClient implements DbConnection {
  private pool: any;

  constructor(connectionString: string) {
    // Production: use pg or better-sqlite3
    this.pool = null;
  }

  async query<T>(sql: string, params: any[] = []): Promise<T[]> {
    // Placeholder - actual implementation uses pg pool
    return [] as T[];
  }

  async execute(sql: string, params: any[] = []): Promise<void> {
    await this.query(sql, params);
  }

  async transaction<T>(fn: (conn: DbConnection) => Promise<T>): Promise<T> {
    await this.execute('BEGIN');
    try {
      const result = await fn(this);
      await this.execute('COMMIT');
      return result;
    } catch (err) {
      await this.execute('ROLLBACK');
      throw err;
    }
  }

  async close(): Promise<void> {
    // Close pool
  }
}

export class ProductRepository implements BaseRepository<Product, string> {
  constructor(private db: DbConnection) {}

  async findById(id: string): Promise<Product | null> {
    const rows = await this.db.query<Product>(
      'SELECT * FROM products WHERE id = $1', [id]
    );
    return rows[0] || null;
  }

  async findAll(): Promise<Product[]> {
    return this.db.query<Product>('SELECT * FROM products');
  }

  async create(entity: Omit<Product, 'id' | 'createdAt'>): Promise<Product> {
    const id = `prod_${Date.now()}`;
    const now = new Date().toISOString();
    await this.db.execute(
      'INSERT INTO products (id, sku, name, description, category_ids, attributes, variants, status, tenant_id, created_at) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10)',
      [id, entity.sku, entity.name, entity.description, JSON.stringify(entity.categoryIds), JSON.stringify(entity.attributes), JSON.stringify(entity.variants), entity.status, entity.tenantId, now]
    );
    return { ...entity, id, createdAt: now };
  }

  async update(id: string, entity: Partial<Product>): Promise<Product | null> {
    const keys = Object.keys(entity);
    if (!keys.length) return this.findById(id);
    
    const setClause = keys.map((k, i) => `${k} = $${i + 2}`).join(', ');
    await this.db.execute(
      `UPDATE products SET ${setClause}, updated_at = NOW() WHERE id = $1`,
      [id, ...Object.values(entity)]
    );
    return this.findById(id);
  }

  async delete(id: string): Promise<boolean> {
    await this.db.execute('DELETE FROM products WHERE id = $1', [id]);
    return true;
  }
}
