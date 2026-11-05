// PreToolUse hook: only let Claude send test traffic to sites listed in SITES.md.
// It checks testing tools in shell commands (curl, wget, Invoke-WebRequest,
// Invoke-RestMethod, playwright codegen/open) and browser navigation tools.
// Every site in SITES.md is built for testing practice; anything else needs the
// owner's permission, so the hook blocks it (exit code 2) and tells Claude why.

const fs = require('fs');
const path = require('path');

// Documentation sites that are fine to open in the browser for research.
const DOC_HOSTS = ['playwright.dev', 'developer.mozilla.org', 'github.com', 'docs.github.com'];
const LOCAL_HOSTS = ['localhost', '127.0.0.1', '[::1]'];
const TEST_TOOLS = /\b(curl|wget|invoke-webrequest|iwr|invoke-restmethod|irm)\b|playwright\s+(codegen|open)\b/i;

const normalize = (host) => host.toLowerCase().replace(/^www\./, '');

function allowedHosts(projectDir) {
  const sites = fs.readFileSync(path.join(projectDir, 'SITES.md'), 'utf8');
  const hosts = [...sites.matchAll(/https?:\/\/([^/\s|)]+)/g)].map((m) => normalize(m[1]));
  return new Set([...hosts, ...LOCAL_HOSTS]);
}

function hostsIn(text) {
  return [...text.matchAll(/https?:\/\/([^/\s'"`|)]+)/gi)].map((m) => normalize(m[1].replace(/:\d+$/, '')));
}

let raw = '';
process.stdin.on('data', (chunk) => (raw += chunk));
process.stdin.on('end', () => {
  const input = JSON.parse(raw || '{}');
  const toolInput = input.tool_input || {};
  const projectDir = process.env.CLAUDE_PROJECT_DIR || input.cwd || process.cwd();

  let hosts = [];
  let allowed;
  if (typeof toolInput.url === 'string') {
    // Browser navigation: SITES.md hosts plus documentation sites.
    if (/^(back|forward)$/i.test(toolInput.url)) process.exit(0);
    const url = /^[a-z]+:\/\//i.test(toolInput.url) ? toolInput.url : `https://${toolInput.url}`;
    hosts = hostsIn(url);
    allowed = new Set([...allowedHosts(projectDir), ...DOC_HOSTS]);
  } else if (typeof toolInput.command === 'string' && TEST_TOOLS.test(toolInput.command)) {
    // Shell testing tools: SITES.md hosts only.
    hosts = hostsIn(toolInput.command);
    allowed = allowedHosts(projectDir);
  } else {
    process.exit(0);
  }

  const blocked = hosts.filter((h) => !allowed.has(h));
  if (blocked.length > 0) {
    console.error(
      `Blocked: ${[...new Set(blocked)].join(', ')} is not in SITES.md. ` +
        'Only test sites that are built for practice. If the user owns this site or has ' +
        'permission to test it, ask them to add it to SITES.md first.',
    );
    process.exit(2);
  }
  process.exit(0);
});
