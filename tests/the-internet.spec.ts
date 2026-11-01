import { test, expect } from '@playwright/test';
import path from 'path';

test.use({ baseURL: 'https://the-internet.herokuapp.com' });

// ---------- Form authentication ----------
test.describe('Authentication', () => {
  async function login(page, user: string, pass: string) {
    await page.goto('/login');
    await page.getByLabel('Username').fill(user);
    await page.getByLabel('Password').fill(pass);
    await page.getByRole('button', { name: 'Login' }).click();
  }
  const flash = page => page.locator('#flash');

  test('TI-AUTH-001 valid login', async ({ page }) => {
    await login(page, 'tomsmith', 'SuperSecretPassword!');
    await expect(page).toHaveURL(/\/secure$/);
    await expect(flash(page)).toContainText('You logged into a secure area!');
  });

  test('TI-AUTH-002 invalid username', async ({ page }) => {
    await login(page, 'wronguser', 'SuperSecretPassword!');
    await expect(flash(page)).toContainText('Your username is invalid!');
    await expect(page).toHaveURL(/\/login$/);
  });

  test('TI-AUTH-003 invalid password', async ({ page }) => {
    await login(page, 'tomsmith', 'wrong');
    await expect(flash(page)).toContainText('Your password is invalid!');
  });

  test('TI-AUTH-004 logout', async ({ page }) => {
    await login(page, 'tomsmith', 'SuperSecretPassword!');
    await page.getByRole('link', { name: 'Logout' }).click();
    await expect(page).toHaveURL(/\/login$/);
    await expect(flash(page)).toContainText('You logged out of the secure area!');
  });
});

test.describe('Basic auth', () => {
  test.use({ httpCredentials: { username: 'admin', password: 'admin' } });
  test('TI-AUTH-005 basic auth with valid credentials', async ({ page }) => {
    await page.goto('/basic_auth');
    await expect(page.getByText('Congratulations! You must have the proper credentials.')).toBeVisible();
  });
});

// ---------- Form controls ----------
test('TI-FORM-001 checkboxes toggle', async ({ page }) => {
  await page.goto('/checkboxes');
  const boxes = page.getByRole('checkbox');
  await expect(boxes.nth(0)).not.toBeChecked();
  await expect(boxes.nth(1)).toBeChecked();
  await boxes.nth(0).check();
  await boxes.nth(1).uncheck();
  await expect(boxes.nth(0)).toBeChecked();
  await expect(boxes.nth(1)).not.toBeChecked();
});

test('TI-FORM-002 dropdown selection', async ({ page }) => {
  await page.goto('/dropdown');
  const dropdown = page.locator('#dropdown');
  await dropdown.selectOption({ label: 'Option 2' });
  await expect(dropdown).toHaveValue('2');
});

test('TI-FORM-003 key press is detected', async ({ page }) => {
  await page.goto('/key_presses');
  // Note: Enter submits the surrounding form and reloads the page, so test with other keys.
  await page.locator('#target').press('a');
  await expect(page.locator('#result')).toHaveText('You entered: A');
  await page.locator('#target').press('Tab');
  await expect(page.locator('#result')).toHaveText('You entered: TAB');
});

test('TI-FORM-004 add and remove elements', async ({ page }) => {
  await page.goto('/add_remove_elements/');
  const add = page.getByRole('button', { name: 'Add Element' });
  for (let i = 0; i < 3; i++) await add.click();
  const del = page.getByRole('button', { name: 'Delete' });
  await expect(del).toHaveCount(3);
  await del.first().click();
  await expect(del).toHaveCount(2);
});

// ---------- JavaScript alerts ----------
test.describe('JavaScript alerts', () => {
  test.beforeEach(async ({ page }) => { await page.goto('/javascript_alerts'); });
  const result = page => page.locator('#result');

  test('TI-ALERT-001 JS alert accepted', async ({ page }) => {
    page.once('dialog', d => d.accept());
    await page.getByRole('button', { name: 'Click for JS Alert' }).click();
    await expect(result(page)).toHaveText('You successfully clicked an alert');
  });

  test('TI-ALERT-002 JS confirm dismissed', async ({ page }) => {
    page.once('dialog', d => d.dismiss());
    await page.getByRole('button', { name: 'Click for JS Confirm' }).click();
    await expect(result(page)).toHaveText('You clicked: Cancel');
  });

  test('TI-ALERT-003 JS prompt with text', async ({ page }) => {
    page.once('dialog', d => d.accept('Hello QA'));
    await page.getByRole('button', { name: 'Click for JS Prompt' }).click();
    await expect(result(page)).toHaveText('You entered: Hello QA');
  });
});

// ---------- Dynamic content ----------
test('TI-DYN-001 hidden element appears after loading', async ({ page }) => {
  await page.goto('/dynamic_loading/1');
  await page.getByRole('button', { name: 'Start' }).click();
  await expect(page.getByRole('heading', { name: 'Hello World!' })).toBeVisible({ timeout: 15_000 });
});

test('TI-DYN-002 element rendered after loading', async ({ page }) => {
  await page.goto('/dynamic_loading/2');
  await expect(page.getByRole('heading', { name: 'Hello World!' })).toHaveCount(0);
  await page.getByRole('button', { name: 'Start' }).click();
  await expect(page.getByRole('heading', { name: 'Hello World!' })).toBeVisible({ timeout: 15_000 });
});

test('TI-DYN-003 remove and enable controls', async ({ page }) => {
  await page.goto('/dynamic_controls');
  await page.getByRole('button', { name: 'Remove' }).click();
  await expect(page.locator('#message')).toHaveText("It's gone!", { timeout: 15_000 });
  await expect(page.getByRole('checkbox')).toHaveCount(0);

  const input = page.locator('#input-example input[type="text"]');
  await expect(input).toBeDisabled();
  await page.getByRole('button', { name: 'Enable' }).click();
  await expect(page.locator('#message')).toHaveText("It's enabled!", { timeout: 15_000 });
  await expect(input).toBeEditable();
});

// ---------- Frames, files, mouse ----------
test('TI-FRAME-001 read nested frames', async ({ page }) => {
  await page.goto('/nested_frames');
  const top = page.frameLocator('frame[name="frame-top"]');
  await expect(top.frameLocator('frame[name="frame-left"]').locator('body')).toHaveText('LEFT');
  await expect(page.frameLocator('frame[name="frame-bottom"]').locator('body')).toHaveText('BOTTOM');
});

test('TI-FILE-001 file upload', async ({ page }) => {
  await page.goto('/upload');
  await page.locator('#file-upload').setInputFiles(path.join(__dirname, 'fixtures', 'sample.txt'));
  await page.getByRole('button', { name: 'Upload' }).click();
  await expect(page.getByRole('heading', { name: 'File Uploaded!' })).toBeVisible();
  await expect(page.locator('#uploaded-files')).toHaveText('sample.txt');
});

test('TI-MOUSE-001 drag and drop swaps boxes', async ({ page }) => {
  await page.goto('/drag_and_drop');
  await expect(page.locator('#column-a header')).toHaveText('A');
  await page.locator('#column-a').dragTo(page.locator('#column-b'));
  await expect(page.locator('#column-a header')).toHaveText('B');
  await expect(page.locator('#column-b header')).toHaveText('A');
});

test('TI-MOUSE-002 hover reveals user info', async ({ page }) => {
  await page.goto('/hovers');
  const first = page.locator('.figure').first();
  await expect(first.getByText('name: user1')).toBeHidden();
  await first.hover();
  await expect(first.getByText('name: user1')).toBeVisible();
  await expect(first.getByRole('link', { name: 'View profile' })).toBeVisible();
});

// ---------- Known defects ----------
test('TI-BUG-CHK-001 all images load (TI-BUG-001)', async ({ page }) => {
  test.fail(true, 'TI-BUG-001: broken images on /broken_images');
  await page.goto('/broken_images');
  const images = page.locator('#content img');
  await expect(images).toHaveCount(3); // guard: never pass on an empty match
  const widths = await images.evaluateAll(imgs => imgs.map(i => (i as HTMLImageElement).naturalWidth));
  expect(widths.every(w => w > 0)).toBe(true);
});
