import { Product, Order, OrderItem, OrderStatus } from '../../domains/types/commerce';

interface ProductServiceParams {
  products: Product[];
  orders: Order[];
}

export class ProductService {
  private products: Map<string, Product> = new Map();
  private orders: Map<string, Order> = new Map();
  private orderSequence = 100000;

  constructor(params: ProductServiceParams) {
    params.products.forEach(p => this.products.set(p.id, p));
    params.orders.forEach(o => this.orders.set(o.id, o));
  }

  async createProduct(data: Omit<Product, 'id' | 'createdAt'>): Promise<Product> {
    const id = `prod_${Date.now()}_${Math.random().toString(36).slice(2)}`;
    const now = new Date().toISOString();
    const product: Product = { ...data, id, createdAt: now };
    this.products.set(id, product);
    return product;
  }

  async getProduct(id: string): Promise<Product | null> {
    return this.products.get(id) || null;
  }

  async listProducts(tenantId: string, page = 1, limit = 20): Promise<{ products: Product[]; total: number }> {
    const tenantProducts = Array.from(this.products.values()).filter(p => p.tenantId === tenantId);
    const total = tenantProducts.length;
    const products = tenantProducts.slice((page - 1) * limit, page * limit);
    return { products, total };
  }

  async createOrder(data: Omit<Order, 'id' | 'orderNumber' | 'createdAt' | 'updatedAt'>): Promise<Order> {
    const id = `ord_${Date.now()}_${Math.random().toString(36).slice(2)}`;
    const orderNumber = `ORD-${++this.orderSequence}`;
    const now = new Date().toISOString();
    
    const subtotal = data.items.reduce((sum, item) => sum + item.quantity * item.unitPrice, 0);
    const order: Order = {
      ...data,
      id,
      orderNumber,
      subtotal,
      tax: subtotal * 0.1,
      discount: 0,
      total: subtotal * 1.1,
      createdAt: now,
      updatedAt: now,
    };
    this.orders.set(id, order);
    return order;
  }

  async getOrder(id: string): Promise<Order | null> {
    return this.orders.get(id) || null;
  }

  async updateOrderStatus(id: string, status: OrderStatus): Promise<Order | null> {
    const order = this.orders.get(id);
    if (!order) return null;
    order.status = status;
    order.updatedAt = new Date().toISOString();
    return order;
  }

  async updateOrderItems(id: string, items: OrderItem[]): Promise<Order | null> {
    const order = this.orders.get(id);
    if (!order) return null;
    order.items = items;
    order.subtotal = items.reduce((sum, item) => sum + item.quantity * item.unitPrice, 0);
    order.total = order.subtotal * 1.1;
    order.updatedAt = new Date().toISOString();
    return order;
  }
}
