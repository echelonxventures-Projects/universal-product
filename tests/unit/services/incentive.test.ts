import { describe, it, expect, beforeEach } from 'vitest';
import { IncentiveService } from '../../services/incentive';
import { Offer } from '../../domains/types/incentive';

describe('IncentiveService', () => {
  let service: IncentiveService;

  beforeEach(() => {
    service = new IncentiveService({ offers: [], coupons: [] });
  });

  describe('createOffer', () => {
    it('should create an offer with unique id', async () => {
      const offer = await service.createOffer({
        code: 'SUMMER25',
        name: 'Summer Sale',
        description: '25% off summer items',
        type: 'discount',
        value: 25,
        currency: 'USD',
        eligibility: { customerSegments: ['all'] },
        conditions: [],
        schedule: { startDate: '2024-06-01', endDate: '2024-08-31' },
        usage: { totalRedemptions: 0 },
        tenantId: 'tenant-1',
      });

      expect(offer.id).toBeDefined();
      expect(offer.code).toBe('SUMMER25');
      expect(offer.status).toBe('draft');
    });
  });

  describe('listOffers', () => {
    it('should filter by tenant', async () => {
      await service.createOffer({
        code: 'OFFER1',
        name: 'Offer 1',
        description: '',
        type: 'discount',
        value: 10,
        currency: 'USD',
        eligibility: { customerSegments: [] },
        conditions: [],
        schedule: { startDate: '2024-01-01', endDate: '2024-12-31' },
        usage: { totalRedemptions: 0 },
        tenantId: 'tenant-1',
      });

      await service.createOffer({
        code: 'OFFER2',
        name: 'Offer 2',
        description: '',
        type: 'discount',
        value: 20,
        currency: 'USD',
        eligibility: { customerSegments: [] },
        conditions: [],
        schedule: { startDate: '2024-01-01', endDate: '2024-12-31' },
        usage: { totalRedemptions: 0 },
        tenantId: 'tenant-2',
      });

      const offers = await service.listOffers('tenant-1');
      expect(offers).toHaveLength(1);
      expect(offers[0].tenantId).toBe('tenant-1');
    });
  });

  describe('activateOffer', () => {
    it('should change offer status to active', async () => {
      const offer = await service.createOffer({
        code: 'INACTIVE',
        name: 'Inactive Offer',
        description: '',
        type: 'discount',
        value: 10,
        currency: 'USD',
        eligibility: { customerSegments: [] },
        conditions: [],
        schedule: { startDate: '2024-01-01', endDate: '2024-12-31' },
        usage: { totalRedemptions: 0 },
        tenantId: 'tenant-1',
      });

      const activated = await service.activateOffer(offer.id);
      expect(activated?.status).toBe('active');
    });
  });

  describe('getValidCoupon', () => {
    it('should return coupon by code', async () => {
      const coupon = await service.createCoupon({
        code: 'SAVE10',
        offerId: 'offer-1',
      });

      const found = await service.getValidCoupon('SAVE10');
      expect(found?.id).toBe(coupon.id);
      expect(found?.status).toBe('unused');
    });

    it('should not return expired coupons', async () => {
      const coupon = await service.createCoupon({
        code: 'EXPIRED',
        offerId: 'offer-1',
      });

      (await service.getValidCoupon('EXPIRED'))!.status = 'redeemed';

      const found = await service.getValidCoupon('EXPIRED');
      expect(found).toBeNull();
    });
  });

  describe('redeemCoupon', () => {
    it('should mark coupon as redeemed', async () => {
      const coupon = await service.createCoupon({
        code: 'REDEEM1',
        offerId: 'offer-1',
      });

      const result = await service.redeemCoupon(coupon.id, 'order-123');
      expect(result).toBe(true);

      const updated = await service.getValidCoupon(coupon.code);
      expect(updated?.status).toBe('redeemed');
    });
  });
});
