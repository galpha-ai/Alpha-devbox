#!/usr/bin/env node
/**
 * ai-bridge — bidirectional prompt channel between AI CLI peers.
 *
 * Peers map four "accounts" onto two locally-authenticated CLIs:
 *   codex        -> Codex CLI  (OpenAI/ChatGPT account), full coding agent
 *   chatgpt      -> Codex CLI  (OpenAI/ChatGPT account), chat-only persona (read-only sandbox)
 *   claude-code  -> Claude CLI (Anthropic/Claude account), full coding agent
 *   claude       -> Claude CLI (Anthropic/Claude account), chat-only persona (read-only tools)
 *
 * Channels are named, persistent, bidirectional sessions. Each channel keeps
 * one native session per peer (codex `exec resume`, claude `--resume`) plus a
 * JSONL transcript, so either side can continue the conversation across turns.
 *
 * Usage:
 *   ai-bridge status
 *   ai-bridge send <peer> "<prompt>" [--channel NAME] [--fresh] [--cwd DIR]
 *                                    [--model M] [--timeout SEC] [--quiet]
 *   ai-bridge relay <peerA> <peerB> --goal "..." [--rounds N] [--driver a|b]
 *                                    [--channel NAME] [--cwd DIR] [--timeout SEC]
 *   ai-bridge channels
 *   ai-bridge log <channel> [--tail N]
 */

import { spawnSync } from 'node:child_process';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';

const PEERS = {
  codex: { bin: 'codex', persona: 'agent' },
  chatgpt: { bin: 'codex', persona: 'chat' },
  'claude-code': { bin: 'claude', persona: 'agent' },
  claude: { bin: 'claude', persona: 'chat' },
};

const CHAT_PERSONA_PREFIX =
  'You are being consulted as a conversational assistant. Answer in plain text. ' +
  'Do not modify files, run commands, or take actions beyond reading, unless the ' +
  'message explicitly asks you to.\n\n';

const DEFAULT_TIMEOUT_SEC = 1200;

function bridgeHome() {
  if (process.env.AI_BRIDGE_HOME) return process.env.AI_BRIDGE_HOME;
  // /workspace is the persistent sandbox root in devbox runner containers.
  if (fs.existsSync('/workspace')) return '/workspace/.ai-bridge';
  return path.join(os.homedir(), '.ai-bridge');
}

function channelPaths(name) {
  const dir = path.join(bridgeHome(), 'channels');
  fs.mkdirSync(dir, { recursive: true });
  const safe = name.replace(/[^A-Za-z0-9._-]/g, '_');
  return {
    meta: path.join(dir, `${safe}.json`),
    transcript: path.join(dir, `${safe}.jsonl`),
  };
}

function loadMeta(name) {
  const { meta } = channelPaths(name);
  try {
    return JSON.parse(fs.readFileSync(meta, 'utf8'));
  } catch {
    return {
      channel: name,
      createdAt: new Date().toISOString(),
      peerSessions: {},
      turns: 0,
    };
  }
}

function saveMeta(name, data) {
  const { meta } = channelPaths(name);
  fs.writeFileSync(meta, JSON.stringify(data, null, 2));
}

function appendTranscript(name, entry) {
  const { transcript } = channelPaths(name);
  fs.appendFileSync(
    transcript,
    JSON.stringify({ ts: new Date().toISOString(), ...entry }) + '\n',
  );
}

function which(bin) {
  const r = spawnSync('which', [bin], { encoding: 'utf8' });
  return r.status === 0 ? r.stdout.trim() : null;
}

function fail(msg) {
  process.stderr.write(`ai-bridge: ${msg}\n`);
  process.exit(1);
}

function parseFlags(argv) {
  const flags = {};
  const positional = [];
  for (let i = 0; i < argv.length; i++) {
    const a = argv[i];
    if (a === '--fresh' || a === '--quiet') {
      flags[a.slice(2)] = true;
    } else if (a.startsWith('--')) {
      flags[a.slice(2)] = argv[++i];
    } else {
      positional.push(a);
    }
  }
  return { flags, positional };
}

// ---------------------------------------------------------------------------
// Peer invocation
// ---------------------------------------------------------------------------

function runCodex(prompt, { sessionId, cwd, model, timeoutSec, chatOnly }) {
  const lastMsgFile = path.join(
    os.tmpdir(),
    `ai-bridge-codex-${process.pid}-${Math.random().toString(36).slice(2)}.txt`,
  );
  const buildArgs = (resumeId) => {
    const args = ['exec'];
    if (resumeId) args.push('resume', resumeId);
    args.push(
      '--json',
      '--output-last-message',
      lastMsgFile,
      '--skip-git-repo-check',
      '--sandbox',
      chatOnly ? 'read-only' : 'workspace-write',
    );
    if (model) args.push('--model', model);
    args.push('-'); // read the prompt from stdin
    return args;
  };
  const input = chatOnly ? CHAT_PERSONA_PREFIX + prompt : prompt;

  let r = spawnSync('codex', buildArgs(sessionId), {
    cwd,
    input,
    encoding: 'utf8',
    timeout: timeoutSec * 1000,
    maxBuffer: 64 * 1024 * 1024,
  });
  // Stale/unknown session: retry once without resume.
  if (sessionId && r.status !== 0) {
    r = spawnSync('codex', buildArgs(null), {
      cwd,
      input,
      encoding: 'utf8',
      timeout: timeoutSec * 1000,
      maxBuffer: 64 * 1024 * 1024,
    });
  }

  const out = (r.stdout || '') + (r.stderr || '');
  // Session/thread id appears in the JSONL event stream; codex versions vary
  // in field naming, so match the common ones.
  const idMatch = out.match(
    /"(?:session_id|thread_id|conversation_id|rollout_id)"\s*:\s*"([0-9a-zA-Z-]{8,})"/,
  );
  let reply = '';
  try {
    reply = fs.readFileSync(lastMsgFile, 'utf8').trim();
  } catch {
    /* fall through */
  }
  try {
    fs.unlinkSync(lastMsgFile);
  } catch {
    /* ignore */
  }
  if (!reply) {
    // Fallback: last agent_message text in the JSONL stream.
    for (const line of (r.stdout || '').split('\n')) {
      try {
        const ev = JSON.parse(line);
        const item = ev.item || ev.msg || ev;
        if (
          (item.type === 'agent_message' ||
            item.item_type === 'agent_message') &&
          (item.text || item.message)
        ) {
          reply = item.text || item.message;
        }
      } catch {
        /* not JSON */
      }
    }
  }
  return {
    reply: reply || (r.stdout || '').trim().slice(-4000),
    sessionId: idMatch ? idMatch[1] : sessionId || null,
    exitCode: r.status,
    error:
      r.status !== 0
        ? (r.stderr || '').trim().slice(-2000) || r.error?.message
        : null,
  };
}

function runClaude(prompt, { sessionId, cwd, model, timeoutSec, chatOnly }) {
  const buildArgs = (resumeId) => {
    const args = ['-p', '--output-format', 'json'];
    if (resumeId) args.push('--resume', resumeId);
    if (model) args.push('--model', model);
    if (chatOnly) {
      args.push('--allowedTools', 'Read,Glob,Grep');
    } else {
      args.push('--dangerously-skip-permissions');
    }
    return args;
  };
  // Prompt goes via stdin: --allowedTools is variadic and would swallow a
  // trailing positional prompt, and stdin also sidesteps argv length limits.
  const input = chatOnly ? CHAT_PERSONA_PREFIX + prompt : prompt;

  let r = spawnSync('claude', buildArgs(sessionId), {
    cwd,
    input,
    encoding: 'utf8',
    timeout: timeoutSec * 1000,
    maxBuffer: 64 * 1024 * 1024,
  });
  if (sessionId && r.status !== 0) {
    r = spawnSync('claude', buildArgs(null), {
      cwd,
      input,
      encoding: 'utf8',
      timeout: timeoutSec * 1000,
      maxBuffer: 64 * 1024 * 1024,
    });
  }

  let reply = '';
  let newSessionId = sessionId || null;
  try {
    const parsed = JSON.parse(r.stdout);
    reply =
      typeof parsed.result === 'string'
        ? parsed.result
        : JSON.stringify(parsed.result);
    if (parsed.session_id) newSessionId = parsed.session_id;
  } catch {
    reply = (r.stdout || '').trim();
  }
  return {
    reply,
    sessionId: newSessionId,
    exitCode: r.status,
    error:
      r.status !== 0
        ? (r.stderr || '').trim().slice(-2000) || r.error?.message
        : null,
  };
}

function sendToPeer(peerName, prompt, opts) {
  const peer = PEERS[peerName];
  if (!peer)
    fail(
      `unknown peer "${peerName}" (expected: ${Object.keys(PEERS).join(', ')})`,
    );
  if (!which(peer.bin)) {
    fail(
      `"${peer.bin}" CLI not found on PATH. ` +
        (peer.bin === 'codex'
          ? 'Install with: npm install -g @openai/codex, then authenticate (see skill docs).'
          : 'Install with: npm install -g @anthropic-ai/claude-code'),
    );
  }

  const channel = opts.channel || peerName;
  const meta = loadMeta(channel);
  const sessionId = opts.fresh ? null : meta.peerSessions[peerName] || null;
  const started = Date.now();

  appendTranscript(channel, { direction: 'out', to: peerName, prompt });

  const runner = peer.bin === 'codex' ? runCodex : runClaude;
  const result = runner(prompt, {
    sessionId,
    cwd: opts.cwd || process.cwd(),
    model: opts.model,
    timeoutSec: Number(opts.timeout) || DEFAULT_TIMEOUT_SEC,
    chatOnly: peer.persona === 'chat',
  });

  const durationMs = Date.now() - started;
  if (result.sessionId) meta.peerSessions[peerName] = result.sessionId;
  meta.turns += 1;
  meta.lastUsedAt = new Date().toISOString();
  saveMeta(channel, meta);
  appendTranscript(channel, {
    direction: 'in',
    from: peerName,
    reply: result.reply,
    exitCode: result.exitCode,
    durationMs,
    ...(result.error ? { error: result.error } : {}),
  });

  return { channel, ...result, durationMs };
}

// ---------------------------------------------------------------------------
// Commands
// ---------------------------------------------------------------------------

function cmdStatus() {
  const lines = [];
  const codexBin = which('codex');
  const claudeBin = which('claude');
  lines.push(
    `codex CLI:  ${codexBin || 'NOT FOUND (npm install -g @openai/codex)'}`,
  );
  lines.push(
    `claude CLI: ${claudeBin || 'NOT FOUND (npm install -g @anthropic-ai/claude-code)'}`,
  );
  const codexAuth = path.join(os.homedir(), '.codex', 'auth.json');
  lines.push(
    `codex auth (ChatGPT/OpenAI account): ${
      fs.existsSync(codexAuth) || process.env.OPENAI_API_KEY
        ? 'configured'
        : `MISSING — mount ${codexAuth} or set OPENAI_API_KEY`
    }`,
  );
  const claudeCreds = path.join(os.homedir(), '.claude', '.credentials.json');
  lines.push(
    `claude auth (Claude/Anthropic account): ${
      fs.existsSync(claudeCreds) ||
      process.env.ANTHROPIC_API_KEY ||
      process.env.CLAUDE_CODE_OAUTH_TOKEN
        ? 'configured'
        : 'MISSING — run claude login, or set ANTHROPIC_API_KEY / CLAUDE_CODE_OAUTH_TOKEN'
    }`,
  );
  lines.push(`bridge home: ${bridgeHome()}`);
  lines.push(`peers: ${Object.keys(PEERS).join(', ')}`);
  process.stdout.write(lines.join('\n') + '\n');
}

function cmdSend(positional, flags) {
  const [peerName, prompt] = positional;
  if (!peerName || !prompt)
    fail('usage: ai-bridge send <peer> "<prompt>" [--channel NAME] ...');
  const res = sendToPeer(peerName, prompt, flags);
  if (!flags.quiet) {
    process.stderr.write(
      `[ai-bridge] peer=${peerName} channel=${res.channel} session=${res.sessionId || 'n/a'} ` +
        `exit=${res.exitCode} ${(res.durationMs / 1000).toFixed(1)}s\n`,
    );
  }
  if (res.error) process.stderr.write(`[ai-bridge] peer error: ${res.error}\n`);
  process.stdout.write((res.reply || '(empty reply)') + '\n');
  process.exit(res.exitCode === 0 ? 0 : 2);
}

function cmdRelay(positional, flags) {
  const [a, b] = positional;
  if (!a || !b || !PEERS[a] || !PEERS[b]) {
    fail(
      `usage: ai-bridge relay <peerA> <peerB> --goal "..." (peers: ${Object.keys(PEERS).join(', ')})`,
    );
  }
  const goal = flags.goal;
  if (!goal) fail('relay requires --goal "..."');
  const rounds = Math.max(1, Math.min(10, Number(flags.rounds) || 3));
  const channel = flags.channel || `relay-${a}-${b}`;
  const driver = flags.driver === 'b' ? b : flags.driver === 'a' ? a : null;
  const opts = { ...flags, channel };

  const frame = (self, other, body, isFirst) => {
    const role = driver
      ? self === driver
        ? `You are the LEAD. You direct ${other}: give it concrete instructions or follow-up requests, and evaluate its work.`
        : `You are the WORKER. Execute the lead agent's instructions and report results concisely.`
      : `You are collaborating as an equal peer with ${other}. Respond to its last message and advance the goal.`;
    return (
      `[ai-bridge relay | goal: ${goal}]\n${role}\n` +
      (isFirst
        ? `This is the first turn — start working toward the goal.`
        : `Message from ${other}:\n---\n${body}\n---`) +
      `\nKeep your reply focused; it will be forwarded verbatim to ${other}.`
    );
  };

  // The driver (or peer A) speaks first.
  let speaker = driver || a;
  let listener = speaker === a ? b : a;
  let lastMsg = null;

  for (let round = 1; round <= rounds; round++) {
    for (const _turn of [0, 1]) {
      const prompt = frame(speaker, listener, lastMsg, lastMsg === null);
      const res = sendToPeer(speaker, prompt, opts);
      process.stdout.write(
        `\n===== round ${round} | ${speaker} -> ${listener} (${(res.durationMs / 1000).toFixed(0)}s) =====\n` +
          `${res.reply || '(empty reply)'}\n`,
      );
      if (res.error)
        process.stderr.write(`[ai-bridge] ${speaker} error: ${res.error}\n`);
      lastMsg = res.reply;
      [speaker, listener] = [listener, speaker];
    }
  }
  process.stderr.write(
    `[ai-bridge] relay done: ${rounds} round(s), transcript at ${channelPaths(channel).transcript}\n`,
  );
}

function cmdChannels() {
  const dir = path.join(bridgeHome(), 'channels');
  if (!fs.existsSync(dir)) return process.stdout.write('(no channels)\n');
  for (const f of fs.readdirSync(dir).filter((f) => f.endsWith('.json'))) {
    try {
      const m = JSON.parse(fs.readFileSync(path.join(dir, f), 'utf8'));
      process.stdout.write(
        `${m.channel}  turns=${m.turns}  peers=[${Object.keys(m.peerSessions).join(',')}]  last=${m.lastUsedAt || m.createdAt}\n`,
      );
    } catch {
      /* skip corrupt */
    }
  }
}

function cmdLog(positional, flags) {
  const [name] = positional;
  if (!name) fail('usage: ai-bridge log <channel> [--tail N]');
  const { transcript } = channelPaths(name);
  if (!fs.existsSync(transcript)) fail(`no transcript for channel "${name}"`);
  const lines = fs.readFileSync(transcript, 'utf8').trim().split('\n');
  const tail = Number(flags.tail) || 20;
  for (const line of lines.slice(-tail)) {
    try {
      const e = JSON.parse(line);
      const who = e.direction === 'out' ? `-> ${e.to}` : `<- ${e.from}`;
      const body = (e.prompt || e.reply || '')
        .replace(/\s+/g, ' ')
        .slice(0, 200);
      process.stdout.write(`${e.ts} ${who}: ${body}\n`);
    } catch {
      /* skip */
    }
  }
}

// ---------------------------------------------------------------------------

const [, , cmd, ...rest] = process.argv;
const { flags, positional } = parseFlags(rest);

switch (cmd) {
  case 'status':
    cmdStatus();
    break;
  case 'send':
    cmdSend(positional, flags);
    break;
  case 'relay':
    cmdRelay(positional, flags);
    break;
  case 'channels':
    cmdChannels();
    break;
  case 'log':
    cmdLog(positional, flags);
    break;
  default:
    fail(
      'usage: ai-bridge <status|send|relay|channels|log> — see SKILL.md for details',
    );
}
