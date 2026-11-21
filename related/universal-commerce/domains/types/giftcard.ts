export interface GiftCard {
  id: string;
  code: string;
  amount: number;
  currency: string;
  balance: number;
  status: 'active' | 'redeemed' | 'expired';
  customerId?: string;
  purchasedAt: string;
  expiresAt?: string;
}

export interface GiftCardRedemption {
  id: string;
  giftCardId: string;
  orderId: string;
  amount: number;
  createdAt: string;
}

export interface GiftCardIssue {
  id: string;
  amount: number;
  currency: string;
  customerId?: string;
  recipientEmail?: string;
  recipientName?: string;
  message?: string;
  status: 'pending' | 'issued' | 'redeemed';
  createdAt: string;
}
