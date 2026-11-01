import { test, expect, Page } from '@playwright/test';

const URL = 'https://www.saucedemo.com/';
const PASSWORD = 'secret_sauce';

async function login(page: Page, username: string, password = PASSWORD) {
  await page.goto(URL);
  await page.getByPlaceholder('Username').fill(username);
  await page.getByPlaceholder('Password').fill(password);
  await page.getByRole('button', { name: 'Login' }).click();
}

const error = (page: Page) => page.getByTestId('error');
const cartBadge = (page: Page) => page.getByTestId('shopping-cart-badge');

async function prices(page: Page): Promise<number[]> {
  const texts = await page.getByTestId('inventory-item-price').allTextContents();
  return texts.map(t => parseFloat(t.replace('$', '')));
}

// ---------- Login ----------
test.describe('Login', () => {
  test('SD-LOGIN-001 valid login with standard_user', async ({ page }) => {
    await login(page, 'standard_user');
    await expect(page).toHaveURL(/inventory\.html/);
    await expect(page.getByTestId('title')).toHaveText('Products');
    await expect(page.getByTestId('inventory-item')).toHaveCount(6);
  });

  test('SD-LOGIN-002 locked-out user cannot log in', async ({ page }) => {
    await login(page, 'locked_out_user');
    await expect(error(page)).toHaveText('Epic sadface: Sorry, this user has been locked out.');
    await expect(page).not.toHaveURL(/inventory/);
  });

  test('SD-LOGIN-003 wrong password', async ({ page }) => {
    await login(page, 'standard_user', 'wrong_pass');
    await expect(error(page)).toHaveText(
      'Epic sadface: Username and password do not match any user in this service');
  });

  test('SD-LOGIN-004 empty username', async ({ page }) => {
    await page.goto(URL);
    await page.getByRole('button', { name: 'Login' }).click();
    await expect(error(page)).toHaveText('Epic sadface: Username is required');
  });

  test('SD-LOGIN-005 empty password', async ({ page }) => {
    await page.goto(URL);
    await page.getByPlaceholder('Username').fill('standard_user');
    await page.getByRole('button', { name: 'Login' }).click();
    await expect(error(page)).toHaveText('Epic sadface: Password is required');
  });

  test('SD-LOGIN-006 inventory is protected without login', async ({ page }) => {
    await page.goto(URL + 'inventory.html');
    await expect(error(page)).toContainText("You can only access '/inventory.html' when you are logged in");
  });
});

// ---------- Sorting ----------
test.describe('Sorting', () => {
  test.beforeEach(async ({ page }) => { await login(page, 'standard_user'); });

  test('SD-SORT-001 price low to high', async ({ page }) => {
    await page.getByTestId('product-sort-container').selectOption('lohi');
    const p = await prices(page);
    expect(p).toEqual([...p].sort((a, b) => a - b));
  });

  test('SD-SORT-002 name Z to A', async ({ page }) => {
    await page.getByTestId('product-sort-container').selectOption('za');
    const names = await page.getByTestId('inventory-item-name').allTextContents();
    expect(names).toEqual([...names].sort().reverse());
  });
});

// ---------- Cart ----------
test.describe('Cart', () => {
  test.beforeEach(async ({ page }) => { await login(page, 'standard_user'); });

  test('SD-CART-001 add item updates badge', async ({ page }) => {
    await page.getByTestId('add-to-cart-sauce-labs-backpack').click();
    await expect(cartBadge(page)).toHaveText('1');
    await expect(page.getByTestId('remove-sauce-labs-backpack')).toBeVisible();
  });

  test('SD-CART-002 remove item clears badge', async ({ page }) => {
    await page.getByTestId('add-to-cart-sauce-labs-backpack').click();
    await page.getByTestId('remove-sauce-labs-backpack').click();
    await expect(cartBadge(page)).toHaveCount(0);
  });
});

// ---------- Checkout ----------
test.describe('Checkout', () => {
  test.beforeEach(async ({ page }) => {
    await login(page, 'standard_user');
    await page.getByTestId('add-to-cart-sauce-labs-backpack').click();
  });

  test('SD-CHK-001 complete purchase end to end', async ({ page }) => {
    await page.getByTestId('add-to-cart-sauce-labs-bike-light').click();
    await page.getByTestId('shopping-cart-link').click();
    await page.getByTestId('checkout').click();
    await page.getByPlaceholder('First Name').fill('John');
    await page.getByPlaceholder('Last Name').fill('Doe');
    await page.getByPlaceholder('Zip/Postal Code').fill('12345');
    await page.getByTestId('continue').click();

    await expect(page.getByTestId('subtotal-label')).toHaveText('Item total: $39.98');
    await expect(page.getByTestId('tax-label')).toHaveText('Tax: $3.20');
    await expect(page.getByTestId('total-label')).toHaveText('Total: $43.18');

    await page.getByTestId('finish').click();
    await expect(page.getByTestId('complete-header')).toHaveText('Thank you for your order!');
  });

  test('SD-CHK-002 first name is required', async ({ page }) => {
    await page.getByTestId('shopping-cart-link').click();
    await page.getByTestId('checkout').click();
    await page.getByTestId('continue').click();
    await expect(error(page)).toHaveText('Error: First Name is required');
  });

  test('SD-CHK-003 postal code is required', async ({ page }) => {
    await page.getByTestId('shopping-cart-link').click();
    await page.getByTestId('checkout').click();
    await page.getByPlaceholder('First Name').fill('John');
    await page.getByPlaceholder('Last Name').fill('Doe');
    await page.getByTestId('continue').click();
    await expect(error(page)).toHaveText('Error: Postal Code is required');
  });
});

// ---------- Session ----------
test('SD-SESS-001 logout returns to login page', async ({ page }) => {
  await login(page, 'standard_user');
  await page.getByRole('button', { name: 'Open Menu' }).click();
  await page.getByTestId('logout-sidebar-link').click();
  await expect(page.getByRole('button', { name: 'Login' })).toBeVisible();
  await page.goBack();
  await expect(page.getByTestId('inventory-item')).toHaveCount(0);
});

// ---------- problem_user: known defects ----------
// test.fail() = "this is expected to fail because of a known bug".
// The test is reported as passing while the bug exists. If the bug is fixed,
// Playwright flags it so you know to remove the annotation.
test.describe('problem_user known bugs', () => {
  test('SD-PROB-001 product images are unique (SD-BUG-001)', async ({ page }) => {
    test.fail(true, 'SD-BUG-001: every product shows the same image');
    await login(page, 'problem_user');
    const images = page.getByTestId('inventory-item').locator('img');
    // Guard: make sure we actually found the images, so an empty match can't "pass".
    await expect(images).toHaveCount(6);
    const srcs = await images.evaluateAll(imgs => imgs.map(i => i.getAttribute('src')));
    expect(new Set(srcs).size).toBe(6);
  });

  test('SD-PROB-002 last name field accepts input', async ({ page }) => {
    test.fail(true, 'Known: Last Name field rejects typing for problem_user');
    await login(page, 'problem_user');
    await page.getByTestId('add-to-cart-sauce-labs-backpack').click();
    await page.getByTestId('shopping-cart-link').click();
    await page.getByTestId('checkout').click();
    await page.getByPlaceholder('Last Name').fill('Doe');
    await expect(page.getByPlaceholder('Last Name')).toHaveValue('Doe', { timeout: 3000 });
  });
});
