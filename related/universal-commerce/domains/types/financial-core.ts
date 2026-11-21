export interface Reconciliation {
  id: string;
  type: string;
  status: 'pending' | 'in-progress' | 'completed';
  createdAt: string;
  completedAt?: string;
}

export interface Commission {
  id: string;
  partyId: string;
  amount: number;
  currency: string;
  status: 'pending' | 'paid';
  createdAt: string;
}

export interface RevenueShare {
  id: string;
  partyId: string;
  rate: number;
  currency: string;
  status: 'active' | 'inactive';
}

export interface Billing {
  id: string;
  customerId: string;
  amount: number;
  currency: string;
  status: 'pending' | 'paid' | 'overdue';
  createdAt: string;
}

export interface Metering {
  id: string;
  customerId: string;
  metric: string;
  usage: number;
  period: string;
}

export interface Invoice {
  id: string;
  customerId: string;
  amount: number;
  currency: string;
  status: 'pending' | 'paid' | 'overdue';
  dueDate: string;
  createdAt: string;
}

export interface Monetization {
  id: string;
  type: string;
  status: 'active' | 'inactive';
  createdAt: string;
}
