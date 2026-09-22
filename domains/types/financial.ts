export interface LedgerAccount {
  id: string;
  name: string;
  type: 'asset' | 'liability' | 'equity' | 'revenue' | 'expense';
  currency: string;
  tenantId: string;
}

export interface Transaction {
  id: string;
  referenceId: string;
  amount: number;
  currency: string;
  debitedAccountId: string;
  creditedAccountId: string;
  description: string;
  status: 'pending' | 'completed' | 'failed' | 'reversed';
  timestamp: string;
}

export interface Payout {
  id: string;
  recipientId: string;
  amount: number;
  currency: string;
  status: 'pending' | 'processing' | 'completed' | 'failed';
  method: 'bank_transfer' | 'wallet' | 'check';
  scheduledDate: string;
  completedDate?: string;
}

export interface Settlement {
  id: string;
  periodStart: string;
  periodEnd: string;
  status: 'pending' | 'completed' | 'disputed';
  entries: SettlementEntry[];
  totalAmount: number;
}

export interface SettlementEntry {
  type: 'commission' | 'revenue_share' | 'fee';
  partyId: string;
  amount: number;
  currency: string;
}
