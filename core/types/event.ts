export interface UCIIEvent {
  id: string;
  type: string;
  source: string;
  tenantId: string;
  timestamp: string;
  payload: Record<string, unknown>;
  metadata: Record<string, string>;
}

export enum EventType {
  // Commerce
  PRODUCT_CREATED = 'commerce.product.created',
  PRODUCT_UPDATED = 'commerce.product.updated',
  ORDER_CREATED = 'commerce.order.created',
  ORDER_UPDATED = 'commerce.order.updated',
  ORDER_COMPLETED = 'commerce.order.completed',
  PAYMENT_PROCESSED = 'commerce.payment.processed',
  
  // Incentive
  OFFER_CREATED = 'incentive.offer.created',
  COUPON_REDEEMED = 'incentive.coupon.redeemed',
  CASHBACK_GRANTED = 'incentive.cashback.granted',
  LOYALTY_POINTS_EARNED = 'incentive.loyalty.points_earned',
  
  // Financial
  SETTLEMENT_COMPLETED = 'financial.settlement.completed',
  PAYOUT_PROCESSED = 'financial.payout.processed',
}

export interface EventPublisher {
  publish(event: UCIIEvent): Promise<void>;
}

export interface EventSubscriber {
  subscribe(eventType: EventType, handler: (event: UCIIEvent) => void): void;
}
