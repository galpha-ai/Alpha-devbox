import path from 'path';

import { describe, expect, it } from 'vitest';

import {
  decodeSessionScopeKey,
  isValidAgentName,
  resolveAgentPath,
  resolveSessionIpcPath,
  resolveSessionPath,
} from './agent-folder.js';

describe('agent name validation', () => {
  it('accepts normal agent names', () => {
    expect(isValidAgentName('main')).toBe(true);
    expect(isValidAgentName('research')).toBe(true);
    expect(isValidAgentName('Team_42')).toBe(true);
  });

  it('rejects traversal and reserved names', () => {
    expect(isValidAgentName('../../etc')).toBe(false);
    expect(isValidAgentName('/tmp')).toBe(false);
    expect(isValidAgentName('global')).toBe(false);
    expect(isValidAgentName('')).toBe(false);
  });

  it('resolves safe paths under agents directory', () => {
    const resolved = resolveAgentPath('research');
    expect(resolved.endsWith(`${path.sep}agents${path.sep}research`)).toBe(
      true,
    );
  });

  it('resolves safe paths under session-scoped data directories', () => {
    const resolved = resolveSessionIpcPath(
      'research',
      'tg:-1001::1700000000.000100::research',
    );
    expect(
      resolved.endsWith(
        `${path.sep}data${path.sep}sessions${path.sep}research${path.sep}${path.basename(path.dirname(resolved))}${path.sep}ipc`,
      ),
    ).toBe(true);
  });

  it('encodes session scope keys into safe directory names', () => {
    const resolved = resolveSessionPath(
      'research',
      'tg:-1001::1700000000.000100::research',
    );
    const encodedKey = path.basename(resolved);
    expect(encodedKey.includes(':')).toBe(false);
    expect(decodeSessionScopeKey(encodedKey)).toBe(
      'tg:-1001::1700000000.000100::research',
    );
  });

  it('throws for unsafe agent names', () => {
    expect(() => resolveAgentPath('../../etc')).toThrow();
    expect(() =>
      resolveSessionIpcPath('/tmp', 'chat::thread::agent'),
    ).toThrow();
  });
});
