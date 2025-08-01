import { test, expect } from '@playwright/test';

// Basic navigation test ensuring admin dashboard loads

test('admin dashboard navigation', async ({ page }) => {
  await page.goto('http://localhost:3030/admin');
  await expect(page).toHaveURL(/\/admin/);
  await expect(page.locator('text=Admin Console')).toBeVisible();
});
