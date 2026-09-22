import { Offer, Coupon, OfferSchedule, OfferUsage } from '../../domains/types/incentive';

interface IncentiveServiceParams {
  offers: Offer[];
  coupons: Coupon[];
}

export class IncentiveService {
  private offers: Map<string, Offer> = new Map();
  private coupons: Map<string, Coupon> = new Map();

  constructor(params: IncentiveServiceParams) {
    params.offers.forEach(o => this.offers.set(o.id, o));
    params.coupons.forEach(c => this.coupons.set(c.id, c));
  }

  async createOffer(data: Omit<Offer, 'id' | 'status' | 'createdAt'>): Promise<Offer> {
    const id = `offer_${Date.now()}_${Math.random().toString(36).slice(2)}`;
    const offer: Offer = {
      ...data,
      id,
      status: 'draft',
      createdAt: new Date().toISOString(),
    };
    this.offers.set(id, offer);
    return offer;
  }

  async getOffer(id: string): Promise<Offer | null> {
    return this.offers.get(id) || null;
  }

  async listOffers(tenantId: string, status?: Offer['status']): Promise<Offer[]> {
    let offers = Array.from(this.offers.values()).filter(o => o.tenantId === tenantId);
    if (status) {
      offers = offers.filter(o => o.status === status);
    }
    return offers;
  }

  async activateOffer(id: string): Promise<Offer | null> {
    const offer = this.offers.get(id);
    if (!offer) return null;
    offer.status = 'active';
    return offer;
  }

  async createCoupon(data: Omit<Coupon, 'id' | 'status'>): Promise<Coupon> {
    const id = `coupon_${Date.now()}_${Math.random().toString(36).slice(2)}`;
    const coupon: Coupon = {
      ...data,
      id,
      status: 'unused',
    };
    this.coupons.set(id, coupon);
    return coupon;
  }

  async getValidCoupon(code: string): Promise<Coupon | null> {
    for (const coupon of this.coupons.values()) {
      if (coupon.code === code && coupon.status === 'unused') {
        return coupon;
      }
    }
    return null;
  }

  async redeemCoupon(id: string, orderId: string): Promise<boolean> {
    const coupon = this.coupons.get(id);
    if (!coupon) return false;
    coupon.status = 'redeemed';
    coupon.orderId = orderId;
    coupon.usedAt = new Date().toISOString();
    return true;
  }

  async isOfferEligible(offer: Offer, context: EligibilityContext): Promise<boolean> {
    if (!offer.eligibility) return true;

    if (offer.eligibility.minOrderValue && context.orderValue < offer.eligibility.minOrderValue) {
      return false;
    }

    if (offer.eligibility.maxRedemptions && offer.usage.totalRedemptions >= offer.eligibility.maxRedemptions) {
      return false;
    }

    return true;
  }
}

interface EligibilityContext {
  customerSegment: string;
  orderValue: number;
  cartItems: string[];
}
