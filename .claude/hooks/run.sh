#!/usr/bin/env bash
# Runs a hook script with the project's virtual environment, so hooks use the same
# Python (and pytest) as the tests. Works on Windows (.venv/Scripts) and macOS/Linux (.venv/bin).
# Usage: run.sh <hook-script.py>   (the hook's JSON input arrives on stdin)
dir="${CLAUDE_PROJECT_DIR:-.}"
py="$dir/.venv/Scripts/python.exe"
[ -x "$py" ] || py="$dir/.venv/bin/python"
if [ ! -x "$py" ]; then
  echo "Hook skipped: no .venv found. Create it with: python -m venv .venv && pip install -r requirements.txt" >&2
  exit 1  # non-blocking: Claude sees the message, the tool call still runs
fi
exec "$py" "$dir/.claude/hooks/$1"
