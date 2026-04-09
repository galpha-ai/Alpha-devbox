/**
 * Devbox Agent Runner
 * Runs inside a container, receives input from run files, and writes output
 * events to run files.
 *
 * Input protocol:
 *   /ipc/runs/<runId>/input.json
 *   IPC:   Follow-up messages written as JSON files to /ipc/input/
 *          Files: {type:"message", text:"..."}.json — polled and consumed
 *          Sentinel: /ipc/input/_close — signals session end
 *
 * Output protocol:
 *   Ordered JSON files in /ipc/runs/<runId>/out/*.json
 *   Completion marker: /ipc/runs/<runId>/done.json
 */

import fs from 'fs';
import path from 'path';
import {
  query,
  HookCallback,
  PreCompactHookInput,
  PreToolUseHookInput,
} from '@anthropic-ai/claude-agent-sdk';
import { fileURLToPath } from 'url';

import {
  collectSecretValues,
  formatForLog,
  sanitizeForLogging,
} from './error-logging.js';
import { logger } from './logger.js';

interface ThinkingConfig {
  type: 'adaptive' | 'enabled' | 'disabled';
  budgetTokens?: number;
}

interface ContainerInput {
  prompt: string;
  sessionKey: string;
  sessionId?: string;
  agentName: string;
  chatJid: string;
  threadId?: string | null;
  isScheduledTask?: boolean;
  assistantName?: string;
  model?: string;
  thinking?: ThinkingConfig;
  effort?: 'low' | 'medium' | 'high' | 'max';
  secrets?: Record<string, string>;
}

interface ContainerOutput {
  status: 'success' | 'error';
  result: string | null;
  newSessionId?: string;
  error?: string;
}

interface RunDonePayload {
  status: 'success' | 'error';
  error?: string;
  details?: unknown;
}

interface SessionEntry {
  sessionId: string;
  fullPath: string;
  summary: string;
  firstPrompt: string;
}

interface SessionsIndex {
  entries: SessionEntry[];
}

interface SDKUserMessage {
  type: 'user';
  message: { role: 'user'; content: string };
  parent_tool_use_id: null;
  session_id: string;
}

const IPC_INPUT_DIR = '/ipc/input';
const IPC_INPUT_CLOSE_SENTINEL = path.join(IPC_INPUT_DIR, '_close');
const IPC_POLL_MS = 500;
const WORKSPACE_DIR = process.env.WORKSPACE_DIR || '/workspace';
const RUN_DIR = process.env.DEVBOX_RUN_DIR || '';
const RUN_INPUT_PATH = path.join(RUN_DIR, 'input.json');
const RUN_OUT_DIR = path.join(RUN_DIR, 'out');
const RUN_DONE_PATH = path.join(RUN_DIR, 'done.json');
let runOutputSeq = 0;

/**
 * Push-based async iterable for streaming user messages to the SDK.
 * Keeps the iterable alive until end() is called, preventing isSingleUserTurn.
 */
class MessageStream {
  private queue: SDKUserMessage[] = [];
  private waiting: (() => void) | null = null;
  private done = false;

  push(text: string): void {
    this.queue.push({
      type: 'user',
      message: { role: 'user', content: text },
      parent_tool_use_id: null,
      session_id: '',
    });
    this.waiting?.();
  }

  end(): void {
    this.done = true;
    this.waiting?.();
  }

  async *[Symbol.asyncIterator](): AsyncGenerator<SDKUserMessage> {
    while (true) {
      while (this.queue.length > 0) {
        yield this.queue.shift()!;
      }
      if (this.done) return;
      await new Promise<void>((r) => {
        this.waiting = r;
      });
      this.waiting = null;
    }
  }
}

function writeJsonAtomic(filePath: string, payload: unknown): void {
  const tempPath = `${filePath}.tmp-${process.pid}-${Date.now()}-${Math.random().toString(36).slice(2, 8)}`;
  fs.writeFileSync(tempPath, JSON.stringify(payload));
  fs.renameSync(tempPath, filePath);
}

function writeOutput(output: ContainerOutput): void {
  runOutputSeq += 1;
  const outPath = path.join(
    RUN_OUT_DIR,
    `${runOutputSeq.toString().padStart(6, '0')}.json`,
  );
  writeJsonAtomic(outPath, output);
}

function writeDone(done: RunDonePayload): void {
  writeJsonAtomic(RUN_DONE_PATH, done);
}

// Legacy log function - use logger directly for new code
function log(message: string): void {
  logger.info(message);
}

function getSessionSummary(
  sessionId: string,
  transcriptPath: string,
): string | null {
  const projectDir = path.dirname(transcriptPath);
  const indexPath = path.join(projectDir, 'sessions-index.json');

  if (!fs.existsSync(indexPath)) {
    logger.debug({ indexPath }, 'Sessions index not found');
    return null;
  }

  try {
    const index: SessionsIndex = JSON.parse(
      fs.readFileSync(indexPath, 'utf-8'),
    );
    const entry = index.entries.find((e) => e.sessionId === sessionId);
    if (entry?.summary) {
      return entry.summary;
    }
  } catch (err) {
    logger.warn({ err, indexPath }, 'Failed to read sessions index');
  }

  return null;
}

/**
 * Archive the full transcript to conversations/ before compaction.
 */
function createPreCompactHook(assistantName?: string): HookCallback {
  return async (input, _toolUseId, _context) => {
    const preCompact = input as PreCompactHookInput;
    const transcriptPath = preCompact.transcript_path;
    const sessionId = preCompact.session_id;

    if (!transcriptPath || !fs.existsSync(transcriptPath)) {
      logger.debug('No transcript found for archiving');
      return {};
    }

    try {
      const content = fs.readFileSync(transcriptPath, 'utf-8');
      const messages = parseTranscript(content);

      if (messages.length === 0) {
        logger.debug('No messages to archive');
        return {};
      }

      const summary = getSessionSummary(sessionId, transcriptPath);
      const name = summary ? sanitizeFilename(summary) : generateFallbackName();

      const conversationsDir = path.join(WORKSPACE_DIR, 'conversations');
      fs.mkdirSync(conversationsDir, { recursive: true });

      const date = new Date().toISOString().split('T')[0];
      const filename = `${date}-${name}.md`;
      const filePath = path.join(conversationsDir, filename);

      const markdown = formatTranscriptMarkdown(
        messages,
        summary,
        assistantName,
      );
      fs.writeFileSync(filePath, markdown);

      logger.info({ filePath }, 'Archived conversation');
    } catch (err) {
      logger.warn({ err }, 'Failed to archive transcript');
    }

    return {};
  };
}

// Secrets to strip from Bash tool subprocess environments.
// These are needed by claude-code for API auth but should never
// be visible to commands Kit runs.
// Note: GH_TOKEN and GITHUB_TOKEN are intentionally NOT stripped —
// they're short-lived GitHub App installation tokens needed by `gh` CLI
// for PR creation and other GitHub operations.
const SECRET_ENV_VARS = [
  'ANTHROPIC_API_KEY',
  'CLAUDE_CODE_OAUTH_TOKEN',
  'DEVBOX_GIT_AUTH_TOKEN',
  'DEVBOX_GIT_AUTH_TOKENS',
  'GITHUB_PAT',
];
const SEED_ONLY_SECRET_ENV_VARS = new Set([
  'DEVBOX_GIT_AUTH_TOKEN',
  'DEVBOX_GIT_AUTH_TOKENS',
]);

function createSanitizeBashHook(): HookCallback {
  return async (input, _toolUseId, _context) => {
    const preInput = input as PreToolUseHookInput;
    const command = (preInput.tool_input as { command?: string })?.command;
    if (!command) return {};

    const unsetPrefix = `unset ${SECRET_ENV_VARS.join(' ')} 2>/dev/null; `;
    return {
      hookSpecificOutput: {
        hookEventName: 'PreToolUse',
        updatedInput: {
          ...(preInput.tool_input as Record<string, unknown>),
          command: unsetPrefix + command,
        },
      },
    };
  };
}

function sanitizeFilename(summary: string): string {
  return summary
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, '-')
    .replace(/^-+|-+$/g, '')
    .slice(0, 50);
}

function generateFallbackName(): string {
  const time = new Date();
  return `conversation-${time.getHours().toString().padStart(2, '0')}${time.getMinutes().toString().padStart(2, '0')}`;
}

interface ParsedMessage {
  role: 'user' | 'assistant';
  content: string;
}

function parseTranscript(content: string): ParsedMessage[] {
  const messages: ParsedMessage[] = [];

  for (const line of content.split('\n')) {
    if (!line.trim()) continue;
    try {
      const entry = JSON.parse(line);
      if (entry.type === 'user' && entry.message?.content) {
        const text =
          typeof entry.message.content === 'string'
            ? entry.message.content
            : entry.message.content
                .map((c: { text?: string }) => c.text || '')
                .join('');
        if (text) messages.push({ role: 'user', content: text });
      } else if (entry.type === 'assistant' && entry.message?.content) {
        const textParts = entry.message.content
          .filter((c: { type: string }) => c.type === 'text')
          .map((c: { text: string }) => c.text);
        const text = textParts.join('');
        if (text) messages.push({ role: 'assistant', content: text });
      }
    } catch {}
  }

  return messages;
}

function formatTranscriptMarkdown(
  messages: ParsedMessage[],
  title?: string | null,
  assistantName?: string,
): string {
  const now = new Date();
  const formatDateTime = (d: Date) =>
    d.toLocaleString('en-US', {
      month: 'short',
      day: 'numeric',
      hour: 'numeric',
      minute: '2-digit',
      hour12: true,
    });

  const lines: string[] = [];
  lines.push(`# ${title || 'Conversation'}`);
  lines.push('');
  lines.push(`Archived: ${formatDateTime(now)}`);
  lines.push('');
  lines.push('---');
  lines.push('');

  for (const msg of messages) {
    const sender = msg.role === 'user' ? 'User' : assistantName || 'Assistant';
    const content =
      msg.content.length > 2000
        ? msg.content.slice(0, 2000) + '...'
        : msg.content;
    lines.push(`**${sender}**: ${content}`);
    lines.push('');
  }

  return lines.join('\n');
}

/**
 * Check for _close sentinel.
 */
function shouldClose(): boolean {
  if (fs.existsSync(IPC_INPUT_CLOSE_SENTINEL)) {
    try {
      fs.unlinkSync(IPC_INPUT_CLOSE_SENTINEL);
    } catch {
      /* ignore */
    }
    return true;
  }
  return false;
}

/**
 * Drain all pending IPC input messages.
 * Returns messages found, or empty array.
 */
function drainIpcInput(): string[] {
  try {
    fs.mkdirSync(IPC_INPUT_DIR, { recursive: true });
    const files = fs
      .readdirSync(IPC_INPUT_DIR)
      .filter((f) => f.endsWith('.json'))
      .sort();

    const messages: string[] = [];
    for (const file of files) {
      const filePath = path.join(IPC_INPUT_DIR, file);
      try {
        const data = JSON.parse(fs.readFileSync(filePath, 'utf-8'));
        fs.unlinkSync(filePath);
        if (data.type === 'message' && data.text) {
          messages.push(data.text);
        }
      } catch (err) {
        logger.warn({ err, file }, 'Failed to process input file');
        try {
          fs.unlinkSync(filePath);
        } catch {
          /* ignore */
        }
      }
    }
    return messages;
  } catch (err) {
    logger.error({ err }, 'IPC drain error');
    return [];
  }
}

/**
 * Wait for a new IPC message or _close sentinel.
 * Returns the messages as a single string, or null if _close.
 */
function waitForIpcMessage(): Promise<string | null> {
  return new Promise((resolve) => {
    const poll = () => {
      if (shouldClose()) {
        resolve(null);
        return;
      }
      const messages = drainIpcInput();
      if (messages.length > 0) {
        resolve(messages.join('\n'));
        return;
      }
      setTimeout(poll, IPC_POLL_MS);
    };
    poll();
  });
}

/**
 * Run a single query and stream results via writeOutput.
 * Uses MessageStream (AsyncIterable) to keep isSingleUserTurn=false,
 * allowing agent teams subagents to run to completion.
 * Also pipes IPC messages into the stream during the query.
 */
async function runQuery(
  prompt: string,
  sessionId: string | undefined,
  mcpServerPath: string,
  containerInput: ContainerInput,
  sdkEnv: Record<string, string | undefined>,
  secretValues: string[],
  resumeAt?: string,
): Promise<{
  newSessionId?: string;
  lastAssistantUuid?: string;
  closedDuringQuery: boolean;
  sdkErrorResult?: unknown;
}> {
  const stream = new MessageStream();
  stream.push(prompt);

  // Poll IPC for follow-up messages and _close sentinel during the query
  let ipcPolling = true;
  let closedDuringQuery = false;
  const pollIpcDuringQuery = () => {
    if (!ipcPolling) return;
    if (shouldClose()) {
      logger.info('Close sentinel detected during query, ending stream');
      closedDuringQuery = true;
      stream.end();
      ipcPolling = false;
      return;
    }
    const messages = drainIpcInput();
    for (const text of messages) {
      logger.info(
        { messageLength: text.length },
        'Piping IPC message into active query',
      );
      stream.push(text);
    }
    setTimeout(pollIpcDuringQuery, IPC_POLL_MS);
  };
  setTimeout(pollIpcDuringQuery, IPC_POLL_MS);

  let newSessionId: string | undefined;
  let lastAssistantUuid: string | undefined;
  let messageCount = 0;
  let resultCount = 0;
  let sdkErrorResult: unknown;

  // Load global CLAUDE.md as additional system context (shared across all groups)
  const globalClaudeMdPath = '/workspace/global/CLAUDE.md';
  let globalClaudeMd: string | undefined;
  if (fs.existsSync(globalClaudeMdPath)) {
    globalClaudeMd = fs.readFileSync(globalClaudeMdPath, 'utf-8');
  }

  // Discover additional directories mounted at /workspace/extra/*
  // These are passed to the SDK so their CLAUDE.md files are loaded automatically
  const extraDirs: string[] = [];
  const extraBase = '/workspace/extra';
  if (fs.existsSync(extraBase)) {
    for (const entry of fs.readdirSync(extraBase)) {
      const fullPath = path.join(extraBase, entry);
      if (fs.statSync(fullPath).isDirectory()) {
        extraDirs.push(fullPath);
      }
    }
  }
  if (extraDirs.length > 0) {
    logger.info(
      { extraDirs: extraDirs.join(', ') },
      'Additional directories discovered',
    );
  }

  try {
    for await (const message of query({
      prompt: stream,
      options: {
        cwd: WORKSPACE_DIR,
        additionalDirectories: extraDirs.length > 0 ? extraDirs : undefined,
        resume: sessionId,
        resumeSessionAt: resumeAt,
        systemPrompt: globalClaudeMd
          ? {
              type: 'preset' as const,
              preset: 'claude_code' as const,
              append: globalClaudeMd,
            }
          : undefined,
        ...(containerInput.model ? { model: containerInput.model } : {}),
        ...(containerInput.thinking ? { thinking: containerInput.thinking } : {}),
        ...(containerInput.effort ? { effort: containerInput.effort } : {}),
        allowedTools: [
          'Bash',
          'Read',
          'Write',
          'Edit',
          'Glob',
          'Grep',
          'WebSearch',
          'WebFetch',
          'Task',
          'TaskOutput',
          'TaskStop',
          'TeamCreate',
          'TeamDelete',
          'SendMessage',
          'TodoWrite',
          'ToolSearch',
          'Skill',
          'NotebookEdit',
          'mcp__devbox__*',
        ],
        env: sdkEnv,
        permissionMode: 'bypassPermissions',
        allowDangerouslySkipPermissions: true,
        includePartialMessages: true,
        settingSources: ['project', 'user'],
        mcpServers: {
          devbox: {
            command: 'node',
            args: [mcpServerPath],
            env: {
              DEVBOX_CHAT_JID: containerInput.chatJid,
              ...(containerInput.threadId
                ? { DEVBOX_THREAD_ID: containerInput.threadId }
                : {}),
              DEVBOX_AGENT_NAME: containerInput.agentName,
            },
          },
        },
        stderr: (data) => process.stderr.write(data),
        hooks: {
          PreCompact: [
            { hooks: [createPreCompactHook(containerInput.assistantName)] },
          ],
          PreToolUse: [{ matcher: 'Bash', hooks: [createSanitizeBashHook()] }],
        },
      },
    })) {
      messageCount++;
      const m = message as any;

      if (message.type === 'stream_event') {
        // Real-time streaming: extract text deltas and print immediately
        const event = m.event;
        if (event?.type === 'content_block_delta') {
          const delta = event.delta;
          if (delta?.type === 'text_delta' && typeof delta.text === 'string') {
            process.stdout.write(delta.text);
          }
        }
      } else if (message.type === 'tool_progress') {
        // Long-running tool progress updates
        if (m.elapsed_time_seconds >= 5) {
          logger.info(
            {
              tool: m.tool_name,
              elapsed_seconds: Math.round(m.elapsed_time_seconds),
            },
            'Tool running',
          );
        }
      } else if (message.type === 'assistant' && 'uuid' in message) {
        lastAssistantUuid = m.uuid;
        const content = m.message?.content;
        if (Array.isArray(content)) {
          for (const block of content) {
            switch (block.type) {
              case 'text':
                // Skip — already streamed via content_block_delta above
                break;
              case 'tool_use': {
                const input = block.input || {};
                const parts: string[] = [];
                if (input.file_path) parts.push(input.file_path);
                if (input.pattern) parts.push(`"${input.pattern}"`);
                if (input.command) parts.push(input.command);
                if (input.query) parts.push(input.query);
                if (input.old_string) parts.push('(edit)');
                const detail =
                  parts.length > 0
                    ? parts.join(' ')
                    : JSON.stringify(input).slice(0, 200);
                logger.info(
                  { tool: block.name, input: detail },
                  'Tool use',
                );
                break;
              }
              case 'thinking':
                const thinkingPreview = (block.thinking || '')
                  .split('\n')[0]
                  .slice(0, 200);
                logger.info({ thinking: thinkingPreview }, 'Thinking');
                break;
              case 'redacted_thinking':
                break;
              case 'search_result':
                logger.info(
                  { title: block.title, source: block.source },
                  'Search result',
                );
                break;
            }
          }
        }
      } else if (message.type === 'user') {
        const content = m.message?.content;
        if (Array.isArray(content)) {
          for (const block of content) {
            if (block.type === 'tool_result') {
              const resultContent = Array.isArray(block.content)
                ? block.content
                : [];
              for (const part of resultContent) {
                if (part.type === 'text' && part.text) {
                  const lines = part.text.split('\n');
                  if (lines.length > 10) {
                    logger.info(
                      { lines: lines.length },
                      'Tool result (truncated)',
                    );
                  } else {
                    logger.info('Tool result');
                  }
                }
              }
            }
          }
        }
      } else if (message.type === 'system' && message.subtype === 'init') {
        newSessionId = message.session_id;
      } else if (message.type === 'result') {
        resultCount++;
        logger.info(
          {
            subtype: m.subtype,
            cost_usd: m.total_cost_usd,
            duration_ms: m.duration_ms,
            num_turns: m.num_turns,
          },
          'Query result',
        );
        if (m.subtype === 'error_during_execution') {
          sdkErrorResult = sanitizeForLogging(m, secretValues);
          logger.error(
            { error: sdkErrorResult },
            'SDK error during execution',
          );
          writeOutput({
            status: 'error',
            result: null,
            newSessionId,
            error: 'SDK error during execution',
          });
        } else {
          const textResult = m.result ?? null;
          writeOutput({
            status: 'success',
            result: textResult || null,
            newSessionId,
          });
        }
      }
    }
  } catch (loopErr) {
    // When the SDK emits an error result and then exits with non-zero,
    // the async iterator throws. If we already captured the SDK error
    // payload, swallow the process-exit error and return normally so
    // main() can write done.json with the correct details.
    if (sdkErrorResult) {
      logger.warn(
        { err: loopErr },
        'SDK process exited after error result',
      );
    } else {
      throw loopErr;
    }
  }

  ipcPolling = false;
  logger.info(
    {
      messageCount,
      resultCount,
      lastAssistantUuid: lastAssistantUuid || 'none',
      closedDuringQuery,
    },
    'Query done',
  );
  return { newSessionId, lastAssistantUuid, closedDuringQuery, sdkErrorResult };
}

async function main(): Promise<void> {
  if (!RUN_DIR) {
    const errorMessage = 'DEVBOX_RUN_DIR is required';
    logger.fatal(errorMessage);
    process.exit(1);
  }

  fs.mkdirSync(RUN_OUT_DIR, { recursive: true });

  let containerInput: ContainerInput;

  try {
    const payload = fs.readFileSync(RUN_INPUT_PATH, 'utf-8');
    // Best effort: remove input file early (contains secrets).
    try {
      fs.unlinkSync(RUN_INPUT_PATH);
    } catch {
      /* ignore */
    }
    containerInput = JSON.parse(payload);
    logger.info(
      {
        agentName: containerInput.agentName,
        sessionKey: containerInput.sessionKey,
        chatJid: containerInput.chatJid,
        isScheduledTask: containerInput.isScheduledTask,
      },
      'Received input for agent',
    );
  } catch (err) {
    const errorMessage = `Failed to parse input: ${err instanceof Error ? err.message : String(err)}`;
    logger.error({ err }, 'Failed to parse input');
    writeOutput({
      status: 'error',
      result: null,
      error: errorMessage,
    });
    writeDone({ status: 'error', error: errorMessage });
    process.exit(1);
  }

  // Build SDK env: merge secrets into process.env for the SDK only.
  // Secrets never touch process.env itself, so Bash subprocesses can't see them.
  const sdkEnv: Record<string, string | undefined> = { ...process.env };
  for (const [key, value] of Object.entries(containerInput.secrets || {})) {
    // Seed-only secrets are consumed by entrypoint.sh before the SDK starts.
    // Keep them out of the SDK environment entirely.
    if (SEED_ONLY_SECRET_ENV_VARS.has(key)) continue;
    sdkEnv[key] = value;
  }

  const __dirname = path.dirname(fileURLToPath(import.meta.url));
  const mcpServerPath = path.join(__dirname, 'ipc-mcp-stdio.js');

  let sessionId = containerInput.sessionId;
  const secretValues = collectSecretValues(containerInput.secrets);
  fs.mkdirSync(IPC_INPUT_DIR, { recursive: true });

  // Clean up stale _close sentinel from previous container runs
  try {
    fs.unlinkSync(IPC_INPUT_CLOSE_SENTINEL);
  } catch {
    /* ignore */
  }

  // Build initial prompt (drain any pending IPC messages too)
  let prompt = containerInput.prompt;
  if (containerInput.isScheduledTask) {
    prompt = `[SCHEDULED TASK - The following message was sent automatically and is not coming directly from the user or group.]\n\n${prompt}`;
  }
  const pending = drainIpcInput();
  if (pending.length > 0) {
    logger.info(
      { count: pending.length },
      'Draining pending IPC messages into initial prompt',
    );
    prompt += '\n' + pending.join('\n');
  }

  // Query loop: run query → wait for IPC message → run new query → repeat
  let resumeAt: string | undefined;
  try {
    while (true) {
      logger.info(
        {
          sessionId: sessionId || 'new',
          resumeAt: resumeAt || 'latest',
        },
        'Starting query',
      );

      const queryResult = await runQuery(
        prompt,
        sessionId,
        mcpServerPath,
        containerInput,
        sdkEnv,
        secretValues,
        resumeAt,
      );
      if (queryResult.newSessionId) {
        sessionId = queryResult.newSessionId;
      }
      if (queryResult.lastAssistantUuid) {
        resumeAt = queryResult.lastAssistantUuid;
      }

      // SDK reported an error during execution (e.g. stale session resume).
      // Write done.json with the SDK error payload so the controller can
      // detect the specific failure type.
      if (queryResult.sdkErrorResult) {
        const errorMessage = 'SDK error during execution';
        logger.error(
          { details: queryResult.sdkErrorResult },
          'SDK error result captured, writing done.json',
        );
        writeDone({
          status: 'error',
          error: errorMessage,
          details: queryResult.sdkErrorResult,
        });
        process.exit(1);
      }

      // If _close was consumed during the query, exit immediately.
      // Don't emit a session-update marker (it would reset the controller's
      // idle timer and cause a 30-min delay before the next _close).
      if (queryResult.closedDuringQuery) {
        logger.info('Close sentinel consumed during query, exiting');
        break;
      }

      // Emit session update so controller can track it
      writeOutput({ status: 'success', result: null, newSessionId: sessionId });

      logger.info('Query ended, waiting for next IPC message');

      // Wait for the next message or _close sentinel
      const nextMessage = await waitForIpcMessage();
      if (nextMessage === null) {
        logger.info('Close sentinel received, exiting');
        break;
      }

      logger.info(
        { messageLength: nextMessage.length },
        'Got new message, starting new query',
      );
      prompt = nextMessage;
    }
    writeDone({ status: 'success' });
  } catch (err) {
    const errorMessage = err instanceof Error ? err.message : String(err);
    const errorDetails = sanitizeForLogging(err, secretValues);
    logger.error({ err, details: errorDetails }, 'Agent error');
    writeOutput({
      status: 'error',
      result: null,
      newSessionId: sessionId,
      error: errorMessage,
    });
    writeDone({ status: 'error', error: errorMessage, details: errorDetails });
    process.exit(1);
  }
}

main();
