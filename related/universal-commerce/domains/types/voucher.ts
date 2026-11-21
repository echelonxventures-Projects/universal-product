export interface Voucher {
  id: string;
  code: string;
  value: number;
  currency: string;
  type: 'fixed' | 'percentage' | 'credit';
  balance: number;
  status: 'active' | 'redeemed' | 'expired';
  customerId?: string;
  createdAt: string;
  expiresAt?: string;
}

export interface VoucherRedemption {
  id: string;
  voucherId: string;
  orderId: string;
  amount: number;
  createdAt: string;
}

export interface VoucherIssue {
  id: string;
  amount: number;
  currency: string;
  customerId?: string;
  recipientEmail?: string;
  reason: string;
  status: 'pending' | 'issued' | 'redeemed';
  createdAt: string;
}
