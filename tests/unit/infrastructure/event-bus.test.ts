import { describe, it, expect, beforeEach } from 'vitest';
import { EventBus } from '../../core/event-bus';
import { EventType, UCIIEvent } from '../../core/types/event';

describe('EventBus', () => {
  let bus: EventBus;

  beforeEach(() => {
    bus = new EventBus();
  });

  describe('publish', () => {
    it('should call all subscribed handlers', async () => {
      const calls: string[] = [];
      
      bus.subscribe(EventType.PRODUCT_CREATED, (event) => {
        calls.push(`handler1:${event.type}`);
      });

      bus.subscribe(EventType.PRODUCT_CREATED, (event) => {
        calls.push(`handler2:${event.type}`);
      });

      const event: UCIIEvent = {
        id: 'evt-1',
        type: EventType.PRODUCT_CREATED,
        source: 'product-service',
        tenantId: 'tenant-1',
        timestamp: new Date().toISOString(),
        payload: { productId: 'prod-1' },
        metadata: {},
      };

      await bus.publish(event);

      expect(calls).toHaveLength(2);
      expect(calls).toContain('handler1:commerce.product.created');
      expect(calls).toContain('handler2:commerce.product.created');
    });

    it('should pass event to handlers', async () => {
      let receivedEvent: UCIIEvent | null = null;

      bus.subscribe(EventType.PRODUCT_CREATED, (event) => {
        receivedEvent = event;
      });

      const event: UCIIEvent = {
        id: 'evt-2',
        type: EventType.PRODUCT_CREATED,
        source: 'product-service',
        tenantId: 'tenant-1',
        timestamp: new Date().toISOString(),
        payload: { productId: 'prod-2' },
        metadata: {},
      };

      await bus.publish(event);

      expect(receivedEvent?.id).toBe(event.id);
      expect(receivedEvent?.payload.productId).toBe('prod-2');
    });

    it('should not fail if handler throws', async () => {
      bus.subscribe(EventType.PRODUCT_CREATED, () => {
        throw new Error('Handler error');
      });

      const event: UCIIEvent = {
        id: 'evt-3',
        type: EventType.PRODUCT_CREATED,
        source: 'product-service',
        tenantId: 'tenant-1',
        timestamp: new Date().toISOString(),
        payload: {},
        metadata: {},
      };

      await expect(bus.publish(event)).resolves.not.toThrow();
    });
  });

  describe('publishAsync', () => {
    it('should allow async handlers', async () => {
      let asyncCalled = false;

      bus.subscribe(EventType.ORDER_COMPLETED, (event) => {
        asyncCalled = true;
      });

      const event: UCIIEvent = {
        id: 'evt-4',
        type: EventType.ORDER_COMPLETED,
        source: 'order-service',
        tenantId: 'tenant-1',
        timestamp: new Date().toISOString(),
        payload: { orderId: 'ord-1' },
        metadata: {},
      };

      await bus.publishAsync(event);

      expect(asyncCalled).toBe(true);
    });
  });
});
