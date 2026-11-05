"""PostToolUse hook: after Claude edits a Python file, run ruff and mypy on it.

Config lives in ruff.toml and mypy.ini at the project root. Exit code 2 sends the
problems back to Claude so it fixes them right away.
"""

import json
import os
import subprocess
import sys
from pathlib import Path

data = json.load(sys.stdin)
file_path = (data.get("tool_input") or {}).get("file_path") or ""
if not file_path.endswith(".py") or not Path(file_path).exists():
    sys.exit(0)

project_dir = Path(os.environ.get("CLAUDE_PROJECT_DIR") or data.get("cwd") or ".")
checks = [
    ("ruff", [sys.executable, "-m", "ruff", "check", "--no-cache", file_path]),
    ("mypy", [sys.executable, "-m", "mypy", "--no-error-summary", file_path]),
]

problems = []
for name, cmd in checks:
    result = subprocess.run(cmd, cwd=project_dir, capture_output=True, text=True, check=False)
    if result.returncode != 0:
        problems.append(f"--- {name} ---\n{(result.stdout + result.stderr).strip()[-2000:]}")

if problems:
    print(f"Lint/type errors in {Path(file_path).name}. Fix these:\n\n" + "\n\n".join(problems), file=sys.stderr)
    sys.exit(2)
sys.exit(0)
