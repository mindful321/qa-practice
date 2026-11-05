"""PreToolUse hook: refuse any edit that adds a fixed sleep to a test file.

Fixed sleeps (page.wait_for_timeout(), time.sleep()) make tests slow and flaky.
CLAUDE.md says to rely on web-first `expect` assertions instead, and this hook turns
that rule into a hard check. Exit code 2 blocks the edit and tells Claude why.
"""

import json
import re
import sys

data = json.load(sys.stdin)
tool_input = data.get("tool_input") or {}
file_path = (tool_input.get("file_path") or "").replace("\\", "/")
if not re.search(r"(^|/)tests/.*\.py$", file_path):
    sys.exit(0)

# Write sends `content`, Edit sends `new_string`, MultiEdit sends `edits[]`.
pieces = [tool_input.get("content"), tool_input.get("new_string")]
pieces += [edit.get("new_string") for edit in tool_input.get("edits") or []]
new_text = "\n".join(p for p in pieces if p)

if re.search(r"\.wait_for_timeout\s*\(|\btime\.sleep\s*\(|^\s*from\s+time\s+import\s+.*\bsleep\b", new_text, re.M):
    print(
        "Blocked: fixed sleeps (wait_for_timeout(), time.sleep()) are not allowed in this repo "
        "(see CLAUDE.md). Wait for a condition instead, for example "
        '`expect(page.get_by_text("Done")).to_be_visible()` or `page.expect_response(...)`.',
        file=sys.stderr,
    )
    sys.exit(2)
sys.exit(0)
