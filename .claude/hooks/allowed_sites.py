"""PreToolUse hook: only let Claude send test traffic to sites listed in SITES.md.

It checks testing tools in shell commands (curl, wget, Invoke-WebRequest,
Invoke-RestMethod, playwright codegen/open) and browser navigation tools.
Every site in SITES.md is built for testing practice; anything else needs the
owner's permission, so the hook blocks it (exit code 2) and tells Claude why.
"""

import json
import os
import re
import sys
from pathlib import Path

# Documentation sites that are fine to open in the browser for research.
DOC_HOSTS = {"playwright.dev", "developer.mozilla.org", "github.com", "docs.github.com", "docs.pytest.org", "docs.python.org"}
LOCAL_HOSTS = {"localhost", "127.0.0.1", "[::1]"}
TEST_TOOLS = re.compile(
    r"\b(curl|wget|invoke-webrequest|iwr|invoke-restmethod|irm)\b|playwright\s+(codegen|open)\b", re.I
)
URL_HOST = re.compile(r"https?://([^/\s'\"`|)]+)", re.I)


def normalize(host: str) -> str:
    host = host.lower()
    if not host.startswith("["):
        host = host.split(":")[0]  # drop a port
    return host.removeprefix("www.")


def hosts_in(text: str) -> list[str]:
    return [normalize(h) for h in URL_HOST.findall(text)]


def allowed_hosts(project_dir: Path) -> set[str]:
    sites = (project_dir / "SITES.md").read_text(encoding="utf-8")
    return set(hosts_in(sites)) | LOCAL_HOSTS


data = json.load(sys.stdin)
tool_input = data.get("tool_input") or {}
project_dir = Path(os.environ.get("CLAUDE_PROJECT_DIR") or data.get("cwd") or ".")

url = tool_input.get("url")
command = tool_input.get("command")
if isinstance(url, str):
    # Browser navigation: SITES.md hosts plus documentation sites.
    if url.lower() in ("back", "forward"):
        sys.exit(0)
    if not re.match(r"^[a-z]+://", url, re.I):
        url = "https://" + url
    hosts = hosts_in(url)
    allowed = allowed_hosts(project_dir) | DOC_HOSTS
elif isinstance(command, str) and TEST_TOOLS.search(command):
    # Shell testing tools: SITES.md hosts only.
    hosts = hosts_in(command)
    allowed = allowed_hosts(project_dir)
else:
    sys.exit(0)

blocked = sorted({h for h in hosts if h not in allowed})
if blocked:
    print(
        f"Blocked: {', '.join(blocked)} is not in SITES.md. Only test sites that are built for practice. "
        "If the user owns this site or has permission to test it, ask them to add it to SITES.md first.",
        file=sys.stderr,
    )
    sys.exit(2)
sys.exit(0)
