import { Product } from '../commerce';

export interface Vendor {
  id: string;
  name: string;
  legalName: string;
  email: string;
  phone?: string;
  status: 'active' | 'inactive';
  products: string[];
  createdAt: string;
}

export interface VendorProfile {
  vendorId: string;
  totalProducts: number;
  totalOrders: number;
  onTimeDelivery: number;
  qualityScore: number;
}

export interface ProductVendor {
  id: string;
  productId: string;
  vendorId: string;
  sku: string;
  price: number;
  minQuantity: number;
  leadTime: number;
  status: 'active' | 'inactive';
}
