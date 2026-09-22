import { test, expect } from '@playwright/test';

test.describe('UCII Admin Portal', () => {
  test('should load dashboard', async ({ page }) => {
    await page.goto('/admin');
    await expect(page.locator('h1')).toContainText('UCII Admin Dashboard');
  });

  test('should navigate to products', async ({ page }) => {
    await page.goto('/admin');
    await page.click('text=Products');
    await expect(page.locator('h1')).toContainText('Products');
  });

  test('should load orders', async ({ page }) => {
    await page.goto('/admin');
    await page.click('text=Orders');
    await expect(page.locator('h1')).toContainText('Orders');
  });
});

test.describe('Product Management', () => {
  test('should create a product', async ({ page }) => {
    await page.goto('/admin/products');
    await page.click('text=New Product');
    
    await page.fill('input[type="text"]', 'TEST-SKU-001');
    await page.fill('textarea', 'Test Product');
    await page.click('text=Create Product');
    
    await expect(page.locator('td')).toContainText('TEST-SKU-001');
  });

  test('should view product list', async ({ page }) => {
    await page.goto('/admin/products');
    await expect(page.locator('table')).toBeVisible();
  });
});

test.describe('Offer Management', () => {
  test('should navigate to offers', async ({ page }) => {
    await page.goto('/admin');
    await page.click('text=Offers');
    await expect(page.locator('h1')).toContainText('Offers');
  });

  test('should create an offer', async ({ page }) => {
    await page.goto('/admin/offers');
    await page.click('text=New Offer');
    await page.fill('input[type="text"]', 'SUMMER25');
    await page.click('button[type="submit"]');
    await expect(page.locator('td')).toContainText('SUMMER25');
  });
});

test.describe('Merchant Portal', () => {
  test('should load merchant dashboard', async ({ page }) => {
    await page.goto('/merchant');
    await expect(page.locator('h1')).toContainText('Merchant Dashboard');
  });

  test('should show earnings', async ({ page }) => {
    await page.goto('/merchant');
    await expect(page.locator('text=Earnings')).toBeVisible();
  });
});

test.describe('Seller Portal', () => {
  test('should load seller dashboard', async ({ page }) => {
    await page.goto('/seller');
    await expect(page.locator('h1')).toContainText('Seller Dashboard');
  });
});
