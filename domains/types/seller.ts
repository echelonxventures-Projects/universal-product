import { Product, Inventory } from '../commerce';

export interface Seller {
  id: string;
  merchantId: string;
  name: string;
  email: string;
  status: 'pending' | 'active' | 'suspended';
  products: string[];
  totalSales: number;
  createdAt: string;
  updatedAt: string;
}

export interface SellerProfile {
  sellerId: string;
  totalOrders: number;
  totalRevenue: number;
  averageRating: number;
  productsCount: number;
  responseTime: number;
}

export interface SellerInventory {
  sellerId: string;
  productId: string;
  quantity: number;
  reserved: number;
  available: number;
}
