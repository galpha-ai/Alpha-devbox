# Spec 003: Slack Typing Indicator via Emoji Reactions

**Status**: Draft
**Author**: devbox-agent
**Date**: 2026-03-12
**Related Issue**: #15

## Problem

When the devbox-agent runner is working on tasks in Slack, users cannot tell if the agent is actively working, waiting for a reply, or has finished processing. This creates uncertainty and a poor user experience.

The `setTyping` method in `src/channels/slack.ts` is currently a no-op because Slack does not provide a general-purpose typing indicator API for bots:

```typescript
async setTyping(_jid: string, _isTyping: boolean): Promise<void> {
  // Slack bots do not have a typing indicator API.
}
```

Users need clear visual feedback showing:
- When the agent starts processing their message
- When the agent finishes successfully
- When the agent encounters an error

## Goals

- Provide clear, deterministic visual feedback for agent processing status
- Use Slack's native reactions API (emoji) as a workaround for missing typing indicator
- Implement status tracking without LLM involvement (fully deterministic)
- Support success and error states, not just "typing"
- Minimal changes to existing architecture

## Non-Goals

- Native typing indicator (not available in Slack Bot API)
- Thread-specific status tracking (track per channel JID for MVP)
- Auto-cleanup of completion emojis (keep for audit trail)
- Customizable emojis per agent (use standard set for MVP)

---

## Research: Available Approaches

### 1. Emoji Reaction Workaround (Chosen)
- Use `reactions.add` API to add processing emoji (⏳) when agent starts
- Use `reactions.remove` + `reactions.add` to change to completion emoji (✅ or ❌)
- Reference: Botpress uses this approach with "Typing indicator emoji" option
- API: https://api.slack.com/methods/reactions.add

**Pros**: Simple, widely understood, works in all message types, deterministic
**Cons**: Requires `reactions:write` scope, less subtle than native typing indicator

### 2. Assistant Threads with Status
- Use `assistant.threads.setStatus` for typing indicators
- Requires `assistant:write` scope and Slack's "Agents and AI Apps" feature
- Reference: https://github.com/openclaw/openclaw/issues/19809

**Pros**: Official Slack AI agent feature
**Cons**: Forces thread-based UI, requires special workspace configuration

### 3. Legacy RTM API
- Send typing events via Real-Time Messaging API
- Reference: https://api.slack.com/legacy/rtm

**Pros**: Native typing indicator
**Cons**: Deprecated by Slack, discouraged for new implementations

**Decision**: Use emoji reaction workaround (option 1) as the most practical solution.

---

## Design

### Status State Machine

```
IDLE → PROCESSING → SUCCESS
                 → ERROR
                 → IDLE (cancelled/interrupted)
```

### Emoji Mapping

| Status      | Emoji                   | Emoji Name               | When Applied                          |
|-------------|-------------------------|--------------------------|---------------------------------------|
| PROCESSING  | ⏳                      | `hourglass_flowing_sand` | Agent starts working on user message  |
| SUCCESS     | ✅                      | `white_check_mark`       | Agent completes without errors        |
| ERROR       | ❌                      | `x`                      | Agent encounters error or failure     |
| IDLE        | (no emoji)              | -                        | No active work (or cleanup)           |

### Architecture Changes

#### 1. Track Triggering Message Timestamp

Add to `SlackChannel` class:

```typescript
private lastUserMessageTs = new Map<string, string>();  // jid -> message timestamp
```

Update in `setupEventHandlers()` when receiving non-bot messages:

```typescript
if (!isBotMessage) {
  this.lastUserMessageTs.set(jid, actualMessage.ts);
}
```

#### 2. Extend `setTyping` Signature

Current signature:
```typescript
setTyping?(jid: string, isTyping: boolean): Promise<void>;
```

New signature:
```typescript
setTyping?(jid: string, status: 'processing' | 'success' | 'error' | 'idle'): Promise<void>;
```

#### 3. Implement Emoji Reactions in `slack.ts`

Replace the no-op implementation with:

```typescript
async setTyping(jid: string, status: 'processing' | 'success' | 'error' | 'idle'): Promise<void> {
  const channelId = jid.replace(/^slack:/, '');
  const messageTs = this.lastUserMessageTs.get(jid);

  if (!messageTs) {
    logger.debug({ jid }, 'No triggering message timestamp for typing indicator');
    return;
  }

  const EMOJI_MAP = {
    processing: 'hourglass_flowing_sand',
    success: 'white_check_mark',
    error: 'x',
    idle: null,  // remove all
  };

  try {
    // Remove all status emojis to ensure clean state
    const allStatusEmojis = ['hourglass_flowing_sand', 'white_check_mark', 'x'];
    for (const emoji of allStatusEmojis) {
      try {
        await this.app.client.reactions.remove({
          channel: channelId,
          name: emoji,
          timestamp: messageTs,
        });
      } catch (err) {
        // Ignore - emoji might not exist, which is fine
      }
    }

    // Add new status emoji if not idle
    const emoji = EMOJI_MAP[status];
    if (emoji) {
      await this.app.client.reactions.add({
        channel: channelId,
        name: emoji,
        timestamp: messageTs,
      });
    }

    logger.debug({ jid, status, emoji }, 'Updated Slack typing indicator');
  } catch (err) {
    logger.debug({ jid, status, err }, 'Failed to update Slack typing indicator');
  }
}
```

#### 4. Update Callers in `index.ts`

**Start Processing** (line ~472):
```typescript
await channel.setTyping?.(chatJid, 'processing');
```

**Resume Processing** (line ~877):
```typescript
channel.setTyping?.(chatJid, 'processing')
  ?.catch((err) =>
    logger.warn({ chatJid, err }, 'Failed to set typing indicator'),
  );
```

**End Processing** (line ~516):
```typescript
const finalStatus = (output.status === 'error' || hadError) ? 'error' : 'success';
await channel.setTyping?.(chatJid, finalStatus);
```

### Sequence Diagram

```
User                Slack               Controller          Runner
 |                    |                      |                 |
 | Send message       |                      |                 |
 |-------------------->|                      |                 |
 |                    |                      |                 |
 |                    | onMessage callback   |                 |
 |                    |--------------------->|                 |
 |                    |                      |                 |
 |                    |                      | Track message   |
 |                    |                      | timestamp       |
 |                    |                      |                 |
 |                    |   Add ⏳ emoji       |                 |
 |                    |<---------------------|                 |
 |                    |                      |                 |
 |                    |                      | Spawn runner    |
 |                    |                      |---------------->|
 |                    |                      |                 |
 |                    |                      |   Agent work    |
 |                    |                      |                 |
 |                    |                      |<-- Output       |
 |                    |                      |                 |
 |                    | Send response        |                 |
 |                    |<---------------------|                 |
 |                    |                      |                 |
 | Receive response   |                      |                 |
 |<--------------------|                      |                 |
 |                    |                      |                 |
 |                    | Remove ⏳, add ✅     |                 |
 |                    |<---------------------|                 |
 |                    |                      |                 |
```

---

## Implementation Plan

### Phase 1: Core Implementation

1. **Update type definitions** (`src/types.ts`)
   - Change `setTyping` signature to accept status enum

2. **Implement tracking** (`src/channels/slack.ts`)
   - Add `lastUserMessageTs` map
   - Track message timestamps in `setupEventHandlers()`

3. **Implement emoji reactions** (`src/channels/slack.ts`)
   - Replace no-op `setTyping` with emoji reaction logic
   - Handle emoji removal and addition atomically

4. **Update callers** (`src/index.ts`)
   - Change `setTyping(jid, true)` to `setTyping(jid, 'processing')`
   - Change `setTyping(jid, false)` to `setTyping(jid, 'success' | 'error')`
   - Determine final status based on `output.status` and `hadError`

### Phase 2: Telegram Compatibility

5. **Update Telegram channel** (`src/channels/telegram.ts`)
   - Adapt existing `setTyping` to new signature
   - Map `processing` → `true`, `success`/`error`/`idle` → `false`

6. **Update tests** (`src/channels/telegram.test.ts`)
   - Fix test calls to use new signature

### Phase 3: Configuration

7. **Update Slack app manifest**
   - Add `reactions:write` scope to bot token scopes
   - Document in deployment instructions

8. **Add logging**
   - Debug logs for emoji operations
   - Track failures without breaking functionality

---

## Testing Plan

### Unit Tests

- `slack.test.ts`: Test emoji reaction logic
  - Verify correct emoji for each status
  - Verify old emoji removed before adding new one
  - Verify graceful handling of missing message timestamp
  - Verify graceful handling of Slack API errors

### Integration Tests

- Local e2e test with Slack:
  - Send message to agent
  - Verify ⏳ appears on user message
  - Wait for agent completion
  - Verify ⏳ replaced with ✅
  - Trigger error scenario
  - Verify ⏳ replaced with ❌

### Manual Testing

- Test in staging Slack workspace:
  - Direct message to agent
  - Group message mentioning agent
  - Multiple rapid messages
  - Agent error scenarios

---

## Rollout Plan

1. **Merge and deploy to staging**
   - Test with staging Slack workspace
   - Verify emoji behavior

2. **Update Slack app scopes**
   - Add `reactions:write` to production Slack app
   - Re-install app if necessary

3. **Deploy to production**
   - Monitor logs for emoji API errors
   - Verify user experience

---

## Metrics

Track in logs:
- Emoji API call success rate
- Emoji API latency
- Missing message timestamp rate (indicates tracking bug)

---

## Future Enhancements

- **Auto-cleanup**: Remove completion emoji after N seconds (optional)
- **Per-agent emoji customization**: Allow agents to configure their status emojis
- **Thread-aware tracking**: Track per thread instead of per channel
- **Multiple simultaneous requests**: Handle overlapping requests in same channel

---

## Alternatives Considered

### Ephemeral Status Messages

Instead of emoji reactions, post ephemeral messages:
- Use `chat.postEphemeral` to show "Agent is thinking..." only to the user
- Delete it when the agent responds

**Rejected because:**
- More complex message lifecycle management
- Can't show success/error status after completion
- Ephemeral messages can be intrusive

### Assistant Threads API

Use Slack's official Assistant API with `assistant.threads.setStatus`:

**Rejected because:**
- Forces all interactions into thread-based UI
- Requires workspace-level "Agents and AI Apps" feature flag
- Less flexible than current message model

---

## References

- [Slack reactions.add API](https://api.slack.com/methods/reactions.add)
- [Slack reactions.remove API](https://api.slack.com/methods/reactions.remove)
- [Botpress Slack Integration](https://www.botpress.com/docs/integrations/integration-guides/slack)
- [Issue #15: Add typing indicator support for Slack agents](https://github.com/galpha-ai/Alpha-devbox/issues/15)
- [slackapi/bolt-js #885: Typing indicator discussion](https://github.com/slackapi/bolt-js/issues/885)
