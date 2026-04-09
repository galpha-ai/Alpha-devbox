import fs from 'fs';
import os from 'os';
import path from 'path';
import { spawnSync } from 'child_process';
import { fileURLToPath } from 'url';
import { describe, expect, it } from 'vitest';

const wrapperPath = path.resolve(
  path.dirname(fileURLToPath(import.meta.url)),
  '../container/gh-wrapper.sh',
);

interface WrapperRunOptions {
  cwd?: string;
  env?: Record<string, string>;
  tokensFileContent?: string;
}

function makeTempDir(): string {
  return fs.mkdtempSync(path.join(os.tmpdir(), 'gh-wrapper-'));
}

function writeExecutable(pathname: string, content: string): void {
  fs.writeFileSync(pathname, content);
  fs.chmodSync(pathname, 0o755);
}

function runWrapper(args: string[], options?: WrapperRunOptions) {
  const fakeGhDir = makeTempDir();
  const fakeGhPath = path.join(fakeGhDir, 'gh-real');
  const tokensPath = path.join(fakeGhDir, 'tokens.json');

  writeExecutable(
    fakeGhPath,
    [
      '#!/bin/bash',
      'set -euo pipefail',
      'printf \'GH_TOKEN=%s\\n\' "${GH_TOKEN:-}"',
      'printf \'GITHUB_TOKEN=%s\\n\' "${GITHUB_TOKEN:-}"',
      'printf \'ARGS=%s\\n\' "$*"',
    ].join('\n'),
  );

  if (options?.tokensFileContent) {
    fs.writeFileSync(tokensPath, options.tokensFileContent, { mode: 0o600 });
  }

  const env = {
    ...process.env,
    ...options?.env,
    DEVBOX_REAL_GH_BIN: fakeGhPath,
    DEVBOX_GH_TOKENS_FILE: tokensPath,
  };

  const result = spawnSync('bash', [wrapperPath, ...args], {
    cwd: options?.cwd,
    env,
    encoding: 'utf8',
  });

  fs.rmSync(fakeGhDir, { recursive: true, force: true });
  return result;
}

function initRepo(remoteUrl: string): string {
  const repoDir = makeTempDir();
  spawnSync('git', ['init'], { cwd: repoDir, encoding: 'utf8' });
  spawnSync('git', ['remote', 'add', 'origin', remoteUrl], {
    cwd: repoDir,
    encoding: 'utf8',
  });
  return repoDir;
}

describe('gh wrapper', () => {
  it('selects the owner token from --repo', () => {
    const result = runWrapper(
      ['pr', 'create', '--repo', 'your-org/ingester'],
      {
        tokensFileContent:
          '{"your-org":"token-a","your-org":"token-b"}',
        env: { GH_TOKEN: 'fallback-token' },
      },
    );

    expect(result.status).toBe(0);
    expect(result.stdout).toContain('GH_TOKEN=token-b');
    expect(result.stdout).toContain('GITHUB_TOKEN=token-b');
  });

  it('falls back to git remote origin when --repo is absent', () => {
    const repoDir = initRepo(
      'https://x-access-token:old@github.com/your-org/devbox-agent.git',
    );
    const result = runWrapper(['pr', 'status'], {
      cwd: repoDir,
      tokensFileContent: '{"your-org":"token-a","your-org":"token-b"}',
    });

    expect(result.status).toBe(0);
    expect(result.stdout).toContain('GH_TOKEN=token-a');
    fs.rmSync(repoDir, { recursive: true, force: true });
  });

  it('preserves the inherited fallback token when no owner match exists', () => {
    const result = runWrapper(['pr', 'list', '--repo', 'unknown/repo'], {
      tokensFileContent: '{"your-org":"token-a"}',
      env: { GH_TOKEN: 'fallback-token' },
    });

    expect(result.status).toBe(0);
    expect(result.stdout).toContain('GH_TOKEN=fallback-token');
    expect(result.stdout).toContain('GITHUB_TOKEN=');
  });
});
