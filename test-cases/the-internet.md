# The Internet (Herokuapp): Test Cases

**URL:** https://the-internet.herokuapp.com. Each page is a separate practice widget.

## Form authentication (/login)
### TI-AUTH-001: Valid login
- **Priority:** P1 · **Type:** Positive
- **Test data:** tomsmith / SuperSecretPassword!
- **Steps:** Open /login, enter the credentials, and click Login.
- **Expected result:** You land on /secure, and the message "You logged into a secure area!" appears.
- **Automated:** yes

### TI-AUTH-002: Invalid username
- **Priority:** P1 · **Type:** Negative
- **Steps:** Log in as wronguser / SuperSecretPassword!.
- **Expected result:** The message "Your username is invalid!" appears, and you stay on /login.
- **Automated:** yes

### TI-AUTH-003: Invalid password
- **Priority:** P1 · **Type:** Negative
- **Steps:** Log in as tomsmith / wrong.
- **Expected result:** The message "Your password is invalid!" appears.
- **Automated:** yes

### TI-AUTH-004: Logout
- **Priority:** P2 · **Type:** Positive
- **Steps:** Log in, then click Logout.
- **Expected result:** You are back on /login with the message "You logged out of the secure area!".
- **Automated:** yes

### TI-AUTH-005: Basic (browser) authentication
- **Priority:** P2 · **Type:** Positive
- **Steps:** Open /basic_auth with the HTTP credentials admin / admin.
- **Expected result:** The page reads "Congratulations! You must have the proper credentials."
- **Automated:** yes

## Form controls
### TI-FORM-001: Checkboxes toggle
- **Priority:** P2 · **Type:** Positive
- **Steps:** Open /checkboxes. Check the 1st box and uncheck the 2nd.
- **Expected result:** The 1st box is checked and the 2nd is unchecked. (By default the 1st starts unchecked and the 2nd starts checked.)
- **Automated:** yes

### TI-FORM-002: Dropdown selection
- **Priority:** P3 · **Type:** Positive
- **Steps:** Open /dropdown and select "Option 2".
- **Expected result:** The dropdown shows Option 2 (value "2").
- **Automated:** yes

### TI-FORM-003: Key press is detected
- **Priority:** P3 · **Type:** Positive
- **Steps:** Open /key_presses, click the input, and press Enter.
- **Expected result:** The page reads "You entered: ENTER".
- **Automated:** yes

### TI-FORM-004: Add and remove elements
- **Priority:** P3 · **Type:** Positive
- **Steps:** Open /add_remove_elements/. Click "Add Element" 3 times, then click one of the Delete buttons.
- **Expected result:** 3 Delete buttons appear, then 2 remain.
- **Automated:** yes

## JavaScript alerts (/javascript_alerts)
### TI-ALERT-001: JS Alert accepted
- **Expected result:** After you accept the alert, the result reads "You successfully clicked an alert".
### TI-ALERT-002: JS Confirm dismissed
- **Expected result:** After you click Cancel, the result reads "You clicked: Cancel".
### TI-ALERT-003: JS Prompt with text
- **Steps:** Type "Hello QA" into the prompt and accept it.
- **Expected result:** The result reads "You entered: Hello QA".
- (All P2, Positive, automated)

## Dynamic content
### TI-DYN-001: Hidden element appears after loading (/dynamic_loading/1)
- **Priority:** P2 · **Type:** Timing
- **Steps:** Click Start and wait for the loading bar to finish.
- **Expected result:** "Hello World!" becomes visible.
- **Automated:** yes

### TI-DYN-002: Element rendered after loading (/dynamic_loading/2)
- Same as TI-DYN-001, except the element doesn't exist in the page at all until loading finishes.

### TI-DYN-003: Remove and enable controls (/dynamic_controls)
- **Steps:** Click Remove, then click Enable.
- **Expected result:** The message "It's gone!" appears and the checkbox is gone. Then "It's enabled!" appears and the text input becomes editable.
- **Automated:** yes

## Frames, files, mouse
### TI-FRAME-001: Read nested frames (/nested_frames)
- **Expected result:** The left frame shows "LEFT" and the bottom frame shows "BOTTOM".
- **Automated:** yes

### TI-FILE-001: File upload (/upload)
- **Test data:** tests/fixtures/sample.txt
- **Expected result:** "File Uploaded!" is shown, followed by the name sample.txt.
- **Automated:** yes

### TI-MOUSE-001: Drag and drop (/drag_and_drop)
- **Steps:** Drag box A onto box B.
- **Expected result:** The boxes swap places, so the first column header now reads "B".
- **Automated:** yes

### TI-MOUSE-002: Hover reveals user info (/hovers)
- **Steps:** Hover over the first avatar.
- **Expected result:** "name: user1" and a "View profile" link appear.
- **Automated:** yes

## Defects (pages with intentional bugs)
### TI-BUG-CHK-001: All images load (/broken_images)
- **Priority:** P2 · **Type:** UI
- **Expected result:** Every image on the page loads (naturalWidth > 0).
- **Automated:** yes (marked as known failure, see TI-BUG-001)
