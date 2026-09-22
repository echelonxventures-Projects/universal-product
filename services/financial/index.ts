import { Transaction, LedgerAccount, Payout } from '../../domains/types/financial';

export class FinancialService {
  private accounts: Map<string, LedgerAccount> = new Map();
  private transactions: Map<string, Transaction> = new Map();
  private payouts: Map<string, Payout> = new Map();
  private transactionSequence = 0;

  async createAccount(account: Omit<LedgerAccount, 'id'>): Promise<LedgerAccount> {
    const id = `acct_${Date.now()}_${Math.random().toString(36).slice(2)}`;
    const newAccount = { ...account, id };
    this.accounts.set(id, newAccount);
    return newAccount;
  }

  async getAccount(id: string): Promise<LedgerAccount | null> {
    return this.accounts.get(id) || null;
  }

  async createTransaction(transaction: Omit<Transaction, 'id' | 'status' | 'timestamp'>): Promise<Transaction> {
    const id = `txn_${++this.transactionSequence}`;
    const now = new Date().toISOString();
    const txn: Transaction = {
      ...transaction,
      id,
      status: 'pending',
      timestamp: now,
    };
    this.transactions.set(id, txn);
    return txn;
  }

  async recordTransaction(
    debitAccountId: string,
    creditAccountId: string,
    amount: number,
    currency: string,
    referenceId: string,
    description: string
  ): Promise<Transaction> {
    const txn = await this.createTransaction({
      referenceId,
      amount,
      currency,
      debitedAccountId: debitAccountId,
      creditedAccountId: creditAccountId,
      description,
    });

    // Mark transaction as completed
    txn.status = 'completed';
    return txn;
  }

  async getTransaction(id: string): Promise<Transaction | null> {
    return this.transactions.get(id) || null;
  }

  async listTransactions(tenantId: string, limit = 50): Promise<Transaction[]> {
    return Array.from(this.transactions.values()).slice(0, limit);
  }

  async createPayout(payout: Omit<Payout, 'id' | 'status'>): Promise<Payout> {
    const id = `payout_${Date.now()}_${Math.random().toString(36).slice(2)}`;
    const newPayout: Payout = {
      ...payout,
      id,
      status: 'pending',
    };
    this.payouts.set(id, newPayout);
    return newPayout;
  }

  async processPayout(id: string): Promise<Payout | null> {
    const payout = this.payouts.get(id);
    if (!payout) return null;

    payout.status = 'completed';
    payout.completedDate = new Date().toISOString();
    return payout;
  }

  async getBalance(accountId: string): Promise<{ currency: string; balance: number }> {
    const account = await this.getAccount(accountId);
    if (!account) return { currency: 'USD', balance: 0 };
    
    let balance = 0;
    for (const txn of this.transactions.values()) {
      if (txn.debitedAccountId === accountId) {
        balance -= txn.amount;
      } else if (txn.creditedAccountId === accountId) {
        balance += txn.amount;
      }
    }

    return { currency: account.currency, balance };
  }
}

export const financialService = new FinancialService();
