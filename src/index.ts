import { EventBus, bus } from './core/event-bus';
import { PolicyEngine, policyEngine } from './core/policy-engine';
import { WorkflowEngine, workflowEngine } from './core/workflow-engine';
import { configLoader } from './core/config-manager';
import { ProductService } from './services/commerce/product';
import { IncentiveService } from './services/incentive';
import { ApiRouter } from './services/handlers/api';

interface UCIIPlatformConfig {
  tenantId: string;
  region: string;
  features: Record<string, boolean>;
}

export class UCIIPlatform {
  private config: UCIIPlatformConfig;
  private eventBus: EventBus;
  private policyEngine: PolicyEngine;
  private workflowEngine: WorkflowEngine;
  private product: ProductService;
  private incentive: IncentiveService;
  private router: ApiRouter;

  constructor(config: UCIIPlatformConfig) {
    this.config = config;
    this.eventBus = bus;
    this.policyEngine = policyEngine;
    this.workflowEngine = workflowEngine;
    this.product = new ProductService({ products: [], orders: [] });
    this.incentive = new IncentiveService({ offers: [], coupons: [] });
    this.router = new ApiRouter();
    this.setupRoutes();
  }

  async initialize(): Promise<void> {
    console.log(`UCII Platform initialized for tenant: ${this.config.tenantId}`);
    await this.loadConfig();
  }

  private async loadConfig(): Promise<void> {
    try {
      const config = await configLoader.load('./config/platform.yaml');
      console.log('Configuration loaded:', config);
    } catch (err) {
      console.warn('Using default configuration');
    }
  }

  private setupRoutes(): void {
    // Product routes
    this.router.post('/products', async (req) => {
      const product = await this.product.createProduct(req as any);
      return { id: product.id, sku: product.sku };
    });

    this.router.get('/products', async () => {
      const { products } = await this.product.listProducts(this.config.tenantId);
      return { products };
    });

    this.router.get('/products/:id', async () => {
      // Would extract ID from path
      return { id: 'prod-1', name: 'Sample Product' };
    });

    // Order routes
    this.router.post('/orders', async (req) => {
      const order = await this.product.createOrder(req as any);
      return { id: order.id, orderNumber: order.orderNumber };
    });

    // Offer routes
    this.router.get('/offers', async () => {
      const offers = await this.incentive.listOffers(this.config.tenantId);
      return { offers };
    });

    this.router.post('/offers', async (req) => {
      const offer = await this.incentive.createOffer(req as any);
      return { id: offer.id, code: offer.code };
    });

    // Coupon routes
    this.router.post('/coupons/validate', async (req) => {
      const { code } = req as { code: string };
      const coupon = await this.incentive.getValidCoupon(code);
      return { valid: !!coupon, code };
    });
  }

  getRouter(): ApiRouter {
    return this.router;
  }

  async shutdown(): Promise<void> {
    console.log('Shutting down UCII Platform');
  }
}

// Export for external use
export { ProductService, IncentiveService };
export * from './core/types/event';
export * from './core/types/policy';
export * from './domains/types/commerce';
export * from './domains/types/incentive';
