"""PostToolUse hook: after Claude edits a test file, ask pytest to collect it.

`pytest --collect-only` imports the file without opening a browser or touching the
network, so it catches syntax errors, bad imports and broken fixtures in about a second.
Exit code 2 sends the error back to Claude so it fixes the file right away.
"""

import json
import os
import re
import subprocess
import sys
from pathlib import Path

data = json.load(sys.stdin)
file_path = (data.get("tool_input") or {}).get("file_path") or ""
normalized = file_path.replace("\\", "/")
if not re.search(r"(^|/)tests/(test_.*|conftest)\.py$", normalized):
    sys.exit(0)

project_dir = Path(os.environ.get("CLAUDE_PROJECT_DIR") or data.get("cwd") or ".")
target = Path(file_path)
# A conftest.py change can break every test file, so collect the whole suite for it.
collect = "tests" if target.name == "conftest.py" else str(target)

result = subprocess.run(
    [sys.executable, "-m", "pytest", "--collect-only", "-q", "-p", "no:cacheprovider", collect],
    cwd=project_dir,
    capture_output=True,
    text=True,
)

if result.returncode != 0:
    output = (result.stdout + "\n" + result.stderr).strip()
    print(f"pytest could not load {target.name}. Fix this before continuing:\n\n{output[-3000:]}", file=sys.stderr)
    sys.exit(2)
sys.exit(0)
