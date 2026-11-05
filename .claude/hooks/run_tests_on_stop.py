"""Stop hook: run the test suite before Claude ends its turn; block the stop on failure.

Skips when no .py file or pytest.ini differs from git HEAD (so chat-only turns stay fast),
and when the hook already blocked once this turn (stop_hook_active), to avoid an endless loop.
XFAIL counts as a pass; XPASS(strict) counts as a failure, per pytest.ini.
"""

import json
import os
import subprocess
import sys
from pathlib import Path

data = json.load(sys.stdin)
if data.get("stop_hook_active"):
    sys.exit(0)

project_dir = Path(os.environ.get("CLAUDE_PROJECT_DIR") or data.get("cwd") or ".")

status = subprocess.run(
    ["git", "status", "--porcelain"], cwd=project_dir, capture_output=True, text=True, check=False
).stdout
changed = [line[3:] for line in status.splitlines()]
if not any(p.endswith(".py") or p.endswith("pytest.ini") for p in changed):
    sys.exit(0)

result = subprocess.run(
    [sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider"],
    cwd=project_dir, capture_output=True, text=True, check=False,
)
if result.returncode != 0:
    output = (result.stdout + "\n" + result.stderr).strip()
    print(
        "Tests failed, so the turn cannot end yet. Decide if it is an app bug or a test bug, "
        f"then fix it (or mark a confirmed app bug xfail):\n\n{output[-4000:]}",
        file=sys.stderr,
    )
    sys.exit(2)
sys.exit(0)
