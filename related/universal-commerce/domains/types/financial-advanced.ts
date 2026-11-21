export interface Funding {
  id: string;
  type: 'loan' | 'investment' | 'grant' | 'credit';
  amount: number;
  currency: string;
  status: 'pending' | 'approved' | 'disbursed' | 'rejected';
  createdAt: string;
}

export interface Budget {
  id: string;
  name: string;
  amount: number;
  currency: string;
  period: string;
  spent: number;
  status: 'active' | 'exhausted';
  createdAt: string;
}

export interface Treasury {
  id: string;
  name: string;
  balance: number;
  currency: string;
  accounts: string[];
}

export interface SettlementBatch {
  id: string;
  periodStart: string;
  periodEnd: string;
  entries: SettlementEntry[];
  totalAmount: number;
  status: 'pending' | 'completed';
}
