export interface CorporateBenefits {
  id: string;
  name: string;
  type: 'health' | 'wellness' | 'transport' | 'education' | 'other';
  description: string;
  status: 'active' | 'inactive';
  eligibleSegments: string[];
  createdAt: string;
}

export interface CorporateOffer {
  id: string;
  benefitsId: string;
  partner: string;
  discount: number;
  currency: string;
  status: 'active' | 'inactive';
}
