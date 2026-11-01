# SauceDemo: Test Cases

**URL:** https://www.saucedemo.com. **Password for all users:** `secret_sauce`

## Login
### SD-LOGIN-001: Valid login with standard_user
- **Priority:** P1 · **Type:** Positive
- **Steps:** 1. Open the login page. 2. Enter `standard_user` / `secret_sauce`. 3. Click Login.
- **Expected result:** Redirects to `/inventory.html`, the title "Products" is shown, and 6 products are listed.
- **Automated:** yes

### SD-LOGIN-002: Locked-out user cannot log in
- **Priority:** P1 · **Type:** Negative
- **Steps:** Log in as `locked_out_user` / `secret_sauce`.
- **Expected result:** You stay on the login page, and the error "Epic sadface: Sorry, this user has been locked out." appears.
- **Automated:** yes

### SD-LOGIN-003: Wrong password
- **Priority:** P1 · **Type:** Negative
- **Steps:** Log in as `standard_user` / `wrong_pass`.
- **Expected result:** The error "Epic sadface: Username and password do not match any user in this service" appears.
- **Automated:** yes

### SD-LOGIN-004: Empty username
- **Priority:** P2 · **Type:** Negative
- **Steps:** Leave both fields empty and click Login.
- **Expected result:** The error "Epic sadface: Username is required" appears.
- **Automated:** yes

### SD-LOGIN-005: Empty password
- **Priority:** P2 · **Type:** Negative
- **Steps:** Enter only the username `standard_user` and click Login.
- **Expected result:** The error "Epic sadface: Password is required" appears.
- **Automated:** yes

### SD-LOGIN-006: Inventory is protected without login
- **Priority:** P1 · **Type:** Negative (security)
- **Steps:** Open `/inventory.html` directly without logging in.
- **Expected result:** You are sent back to the login page, and the error "...You can only access '/inventory.html' when you are logged in." appears.
- **Automated:** yes

## Inventory and sorting
### SD-SORT-001: Sort by price, low to high
- **Priority:** P2 · **Type:** Positive
- **Preconditions:** Logged in as standard_user.
- **Steps:** Choose "Price (low to high)" in the sort dropdown.
- **Expected result:** Prices are in ascending order (7.99 … 49.99).
- **Automated:** yes

### SD-SORT-002: Sort by name, Z to A
- **Priority:** P3 · **Type:** Positive
- **Steps:** Choose "Name (Z to A)".
- **Expected result:** Names are in descending alphabetical order.
- **Automated:** yes

## Cart
### SD-CART-001: Add an item updates the cart badge
- **Priority:** P1 · **Type:** Positive
- **Steps:** Click "Add to cart" on Sauce Labs Backpack.
- **Expected result:** The cart badge shows 1, and the button changes to "Remove".
- **Automated:** yes

### SD-CART-002: Remove an item clears the badge
- **Priority:** P2 · **Type:** Positive
- **Steps:** Add the Backpack, then click "Remove".
- **Expected result:** The cart badge disappears.
- **Automated:** yes

## Checkout
### SD-CHK-001: Complete a purchase end to end
- **Priority:** P1 · **Type:** Positive
- **Test data:** Backpack ($29.99) + Bike Light ($9.99); John / Doe / 12345
- **Steps:** Add both items, open the cart, click Checkout, fill in the info, click Continue, check the totals, click Finish.
- **Expected result:** Item total is $39.98, Tax is $3.20, and Total is $43.18. "Thank you for your order!" is shown.
- **Automated:** yes

### SD-CHK-002: Checkout requires first name
- **Priority:** P2 · **Type:** Negative
- **Steps:** Add an item, go to checkout, and click Continue with all fields empty.
- **Expected result:** The error "Error: First Name is required" appears.
- **Automated:** yes

### SD-CHK-003: Checkout requires postal code
- **Priority:** P2 · **Type:** Negative
- **Steps:** Fill in the first and last names, leave the postal code empty, and click Continue.
- **Expected result:** The error "Error: Postal Code is required" appears.
- **Automated:** yes

## Session
### SD-SESS-001: Logout
- **Priority:** P1 · **Type:** Positive
- **Steps:** Open the menu and click Logout.
- **Expected result:** You are back on the login page. Pressing Back must not show the inventory without an error.
- **Automated:** yes

## problem_user (known-buggy account)
### SD-PROB-001: Product images match their products
- **Priority:** P2 · **Type:** UI
- **Steps:** Log in as `problem_user` and look at the inventory images.
- **Expected result:** Each product shows its own, different image.
- **Automated:** yes (marked as known failure, see SD-BUG-001)

### SD-PROB-002: Last name field accepts input
- **Priority:** P1 · **Type:** Negative/UI
- **Steps:** As problem_user, add an item, go to checkout, and type "Doe" into Last Name.
- **Expected result:** The Last Name field contains "Doe".
- **Automated:** yes (marked as known failure; log it as SD-BUG-002 once you confirm it yourself)
