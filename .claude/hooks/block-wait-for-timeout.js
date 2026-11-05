// PreToolUse hook: refuse any edit that adds waitForTimeout() to a test file.
// Fixed sleeps make tests slow and flaky. CLAUDE.md says to rely on web-first
// `expect` assertions instead, and this hook turns that rule into a hard check.
// Exit code 2 blocks the edit and tells Claude why.

let raw = '';
process.stdin.on('data', (chunk) => (raw += chunk));
process.stdin.on('end', () => {
  const input = JSON.parse(raw || '{}');
  const toolInput = input.tool_input || {};
  const filePath = (toolInput.file_path || '').replace(/\\/g, '/');
  if (!/(^|\/)tests\/.*\.ts$/.test(filePath)) process.exit(0);

  // Write sends `content`, Edit sends `new_string`, MultiEdit sends `edits[]`.
  const newText = [
    toolInput.content,
    toolInput.new_string,
    ...(toolInput.edits || []).map((e) => e.new_string),
  ]
    .filter(Boolean)
    .join('\n');

  if (/\.waitForTimeout\s*\(/.test(newText)) {
    console.error(
      'Blocked: waitForTimeout() is not allowed in this repo (see CLAUDE.md). ' +
        'Wait for a condition instead, for example ' +
        "`await expect(page.getByText('Done')).toBeVisible()` or `page.waitForResponse(...)`.",
    );
    process.exit(2);
  }
  process.exit(0);
});
