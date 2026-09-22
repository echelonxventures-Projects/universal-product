import { Offer } from './incentive';

export interface Promotion {
  id: string;
  name: string;
  description: string;
  type: 'campaign' | 'event' | 'seasonal';
  status: 'draft' | 'active' | 'paused' | 'completed';
  offers: string[];
  startDate: string;
  endDate: string;
  targetAudience: string[];
  budget: number;
  currency: string;
  createdAt: string;
  updatedAt: string;
}

export interface PromotionCampaign {
  id: string;
  promotionId: string;
  channel: 'email' | 'sms' | 'push' | 'web';
  status: 'scheduled' | 'active' | 'completed';
  createdAt: string;
}
