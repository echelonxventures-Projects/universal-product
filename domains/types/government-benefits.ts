export interface GovernmentBenefits {
  id: string;
  program: string;
  name: string;
  description: string;
  agency: string;
  status: 'active' | 'inactive';
  eligibilityCriteria: Record<string, unknown>;
  createdAt: string;
}

export interface GovernmentIncentive {
  id: string;
  benefitsId: string;
  type: 'subsidy' | 'tax-credit' | 'grant' | 'voucher';
  value: number;
  currency: string;
  status: 'active' | 'inactive';
}
