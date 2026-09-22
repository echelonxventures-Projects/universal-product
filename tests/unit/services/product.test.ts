import { describe, it, expect, beforeEach } from 'vitest';
import { ProductService } from '../../services/commerce/product';
import { Product, OrderItem, OrderStatus } from '../../domains/types/commerce';

describe('ProductService', () => {
  let service: ProductService;

  beforeEach(() => {
    service = new ProductService({ products: [], orders: [] });
  });

  describe('createProduct', () => {
    it('should create a product with unique id', async () => {
      const product = await service.createProduct({
        sku: 'TEST-001',
        name: 'Test Product',
        description: 'A test product',
        categoryIds: ['cat-1'],
        attributes: { color: 'red' },
        variants: [],
        status: 'active',
        tenantId: 'tenant-1',
      });

      expect(product.id).toBeDefined();
      expect(product.sku).toBe('TEST-001');
      expect(product.name).toBe('Test Product');
    });

    it('should validate required fields', async () => {
      await expect(service.createProduct({
        sku: '',
        name: '',
        description: '',
        categoryIds: [],
        attributes: {},
        variants: [],
        status: 'draft',
        tenantId: 'tenant-1',
      })).resolves.toBeTruthy();
    });
  });

  describe('getProduct', () => {
    it('should return null for non-existent product', async () => {
      const product = await service.getProduct('non-existent');
      expect(product).toBeNull();
    });

    it('should return product by id', async () => {
      const created = await service.createProduct({
        sku: 'TEST-002',
        name: 'Product 2',
        description: '',
        categoryIds: [],
        attributes: {},
        variants: [],
        status: 'active',
        tenantId: 'tenant-1',
      });

      const retrieved = await service.getProduct(created.id);
      expect(retrieved).toEqual(created);
    });
  });

  describe('listProducts', () => {
    it('should filter by tenant', async () => {
      await service.createProduct({
        sku: 'TEST-T1-1',
        name: 'Tenant 1 Product',
        description: '',
        categoryIds: [],
        attributes: {},
        variants: [],
        status: 'active',
        tenantId: 'tenant-1',
      });

      await service.createProduct({
        sku: 'TEST-T2-1',
        name: 'Tenant 2 Product',
        description: '',
        categoryIds: [],
        attributes: {},
        variants: [],
        status: 'active',
        tenantId: 'tenant-2',
      });

      const { products } = await service.listProducts('tenant-1');
      expect(products).toHaveLength(1);
      expect(products[0].tenantId).toBe('tenant-1');
    });

    it('should paginate results', async () => {
      for (let i = 0; i < 25; i++) {
        await service.createProduct({
          sku: `TEST-PAGE-${i}`,
          name: `Product ${i}`,
          description: '',
          categoryIds: [],
          attributes: {},
          variants: [],
          status: 'active',
          tenantId: 'tenant-1',
        });
      }

      const page1 = await service.listProducts('tenant-1', 1, 10);
      const page2 = await service.listProducts('tenant-1', 2, 10);

      expect(page1.products).toHaveLength(10);
      expect(page2.products).toHaveLength(10);
      expect(page1.products[0].name).not.toBe(page2.products[0].name);
    });
  });

  describe('createOrder', () => {
    it('should create order with calculated totals', async () => {
      const items: OrderItem[] = [
        { productId: 'prod-1', quantity: 2, unitPrice: 50, totalPrice: 100 },
        { productId: 'prod-2', quantity: 1, unitPrice: 25, totalPrice: 25 },
      ];

      const order = await service.createOrder({
        customerId: 'cust-1',
        status: 'pending' as OrderStatus,
        items,
        shippingAddress: { street: '123 Main St', city: 'Boston', country: 'US', postalCode: '02101' },
        billingAddress: { street: '123 Main St', city: 'Boston', country: 'US', postalCode: '02101' },
        tenantId: 'tenant-1',
      });

      expect(order.orderNumber).toMatch(/^ORD-\d+$/);
      expect(order.subtotal).toBe(125);
      expect(order.total).toBe(137.5);
    });
  });

  describe('updateOrderStatus', () => {
    it('should update order status', async () => {
      const order = await service.createOrder({
        customerId: 'cust-1',
        status: 'pending' as OrderStatus,
        items: [],
        shippingAddress: { street: '', city: '', country: '', postalCode: '' },
        billingAddress: { street: '', city: '', country: '', postalCode: '' },
        tenantId: 'tenant-1',
      });

      const updated = await service.updateOrderStatus(order.id, 'confirmed' as OrderStatus);
      expect(updated?.status).toBe('confirmed');
    });
  });
});
