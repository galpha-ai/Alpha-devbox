import fs from 'fs';
import os from 'os';
import path from 'path';
import { afterEach, describe, expect, it } from 'vitest';
import { spawnSync } from 'child_process';

const repoRoot = path.resolve(__dirname, '..');
const scriptPath = path.join(repoRoot, 'scripts', 'dev-web-local.sh');

const tempDirs: string[] = [];

function makeTempDir(prefix: string): string {
  const dir = fs.mkdtempSync(path.join(os.tmpdir(), prefix));
  tempDirs.push(dir);
  return dir;
}

function writeExecutable(dir: string, name: string, body: string): void {
  const target = path.join(dir, name);
  fs.writeFileSync(target, body, { mode: 0o755 });
}

function setupFakeBin(): string {
  const binDir = makeTempDir('devbox-fake-bin-');
  const shellHeader = '#!/usr/bin/env bash\nset -euo pipefail\n';

  writeExecutable(
    binDir,
    'docker',
    `${shellHeader}if [[ "${'$'}{1:-}" == "info" ]]; then exit 0; fi\nif [[ "${'$'}{1:-}" == "ps" ]]; then exit 0; fi\nexit 0\n`,
  );
  writeExecutable(binDir, 'npm', `${shellHeader}exit 0\n`);
  writeExecutable(binDir, 'npx', `${shellHeader}exit 0\n`);
  writeExecutable(binDir, 'curl', `${shellHeader}exit 0\n`);
  writeExecutable(binDir, 'lsof', `${shellHeader}exit 0\n`);
  writeExecutable(binDir, 'pkill', `${shellHeader}exit 0\n`);

  return binDir;
}

function runDevScript(overrides: Record<string, string | undefined>) {
  const fakeBin = setupFakeBin();
  const dataRoot = makeTempDir('devbox-data-root-');
  fs.mkdirSync(path.join(dataRoot, 'store'), { recursive: true });
  fs.writeFileSync(path.join(dataRoot, 'sentinel.txt'), 'keep-me');

  const result = spawnSync('bash', [scriptPath], {
    cwd: repoRoot,
    encoding: 'utf8',
    env: {
      ...process.env,
      PATH: `${fakeBin}:${process.env.PATH}`,
      DEVBOX_LOCAL_ENV_FILES: path.join(fakeBin, 'missing.env'),
      DEVBOX_DATA_ROOT: dataRoot,
      ANTHROPIC_API_KEY: 'test-key',
      ...overrides,
    },
    timeout: 15_000,
  });

  if (result.error) {
    throw result.error;
  }

  return {
    ...result,
    dataRoot,
    sentinelPath: path.join(dataRoot, 'sentinel.txt'),
  };
}

afterEach(() => {
  for (const dir of tempDirs.splice(0)) {
    fs.rmSync(dir, { recursive: true, force: true });
  }
});

describe('scripts/dev-web-local.sh', () => {
  it('preserves the local data root even if the legacy clean flag is set', () => {
    const result = runDevScript({ DEVBOX_WEB_CLEAN: '1' });

    expect(result.status).toBe(0);
    expect(fs.existsSync(result.sentinelPath)).toBe(true);
  });

  it('preserves the local data root by default', () => {
    const result = runDevScript({ DEVBOX_WEB_CLEAN: undefined });

    expect(result.status).toBe(0);
    expect(fs.existsSync(result.sentinelPath)).toBe(true);
  });
});
