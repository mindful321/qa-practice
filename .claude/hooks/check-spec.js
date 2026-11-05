// PostToolUse hook: after Claude edits a spec file, ask Playwright to list its tests.
// `playwright test --list` compiles the file without opening a browser or touching the
// network, so it catches syntax errors, bad imports and duplicate test titles in about a second.
// Exit code 2 sends the error back to Claude so it fixes the file right away.

const { spawnSync } = require('child_process');
const path = require('path');

let raw = '';
process.stdin.on('data', (chunk) => (raw += chunk));
process.stdin.on('end', () => {
  const input = JSON.parse(raw || '{}');
  const filePath = input.tool_input?.file_path;
  if (!filePath || !/\.spec\.ts$/.test(filePath)) process.exit(0);

  const projectDir = process.env.CLAUDE_PROJECT_DIR || input.cwd || process.cwd();
  const relative = path.relative(projectDir, filePath).split(path.sep).join('/');

  const result = spawnSync('npx', ['playwright', 'test', '--list', relative], {
    cwd: projectDir,
    encoding: 'utf8',
    shell: process.platform === 'win32', // npx is a .cmd file on Windows
  });

  if (result.status !== 0) {
    const output = `${result.stdout || ''}\n${result.stderr || ''}`.trim();
    console.error(`Playwright could not load ${relative}. Fix this before continuing:\n\n${output}`);
    process.exit(2);
  }
  process.exit(0);
});
