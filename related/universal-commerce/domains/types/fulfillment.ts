import { Order } from './commerce';
import { ShippingAddress, ShippingMethod } from './checkout';

export interface Fulfillment {
  id: string;
  orderId: string;
  items: FulfillmentItem[];
  status: 'pending' | 'processing' | 'shipped' | 'delivered' | 'cancelled';
  shippingAddress: ShippingAddress;
  shippingMethod: ShippingMethod;
  tracking?: Tracking;
  estimatedDelivery?: string;
  actualDelivery?: string;
  createdAt: string;
  updatedAt: string;
}

export interface FulfillmentItem {
  productId: string;
  variantId?: string;
  quantity: number;
  serialNumber?: string;
  batchNumber?: string;
  expiryDate?: string;
}

export interface Tracking {
  id: string;
  carrier: string;
  number: string;
  url?: string;
  status: 'pre-transit' | 'in-transit' | 'out-for-delivery' | 'delivered' | 'exception' | 'lost';
  events: TrackingEvent[];
  estimatedDelivery?: string;
}

export interface TrackingEvent {
  timestamp: string;
  location: string;
  status: string;
  description: string;
}

export interface Shipment {
  id: string;
  fulfillmentId: string;
  tracking: Tracking;
  packaging: Packaging;
  carrier: string;
  serviceLevel: string;
  insurance: number;
  cost: number;
  createdAt: string;
  shippedAt?: string;
}

export interface Packaging {
  type: 'box' | 'envelope' | 'tube' | 'custom';
  dimensions?: { length: number; width: number; height: number };
  weight?: number;
}
