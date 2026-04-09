# 004: Web Channel Support

## Status

Draft

## Problem

devbox-agent currently only accepts input from Telegram and Slack. There is no HTTP/WebSocket interface for web frontends. To provide conversation capabilities through the existing your-org web platform, a new channel adapter is needed.

## Goals

- Add a `WebChannel` that exposes HTTP REST + WebSocket endpoints
- Multi-conversation model: each user can have multiple concurrent conversations
- Deploy behind the existing Envoy proxy, reusing the your-org JWT authentication flow (Envoy validates JWT, injects `X-User-Id`)
- Notify users when the global concurrency limit is reached (queue position)
- Deploy to the existing GKE staging cluster alongside current Telegram/Slack channels

## Non-Goals

- Per-user fairness or rate limiting (Envoy-level rate limiting is a future addition)
- Replacing or modifying the runner container model
- Frontend implementation
- Envoy configuration changes (separate PR in your-infra-repo)

---

## Architecture

### Session Mapping

Web conversations map to the existing `SessionScope` triple:

| Field | Value | Source |
|-------|-------|--------|
| `channelId` | `"web:{userId}"` | `X-User-Id` header injected by Envoy after JWT validation |
| `threadId` | `"{conversationId}"` | Client-generated UUID per conversation |
| `agentName` | Config-bound agent name | `web:*` channel binding in config.yaml |

Each conversation is a thread-scoped session. All existing session lifecycle behavior applies: 6h GC, startup recovery, stale-session detection.

### WebChannel

Implements the `Channel` interface. Internally runs:

- **HTTP server** (Node.js `http.createServer`) — REST API endpoints
- **WebSocket server** (`ws` library) — handles upgrade from the same HTTP server

Connection state: `Map<userId, WebSocket>` tracks one active WS connection per user.

### Message Flow

```
Web frontend
  │
  ├── REST: POST /api/devbox/conversations/:id/messages
  │     └── Envoy validates JWT, injects X-User-Id
  │           └── WebChannel.handleMessage()
  │                 └── onMessage(chatJid="web:{userId}", msg)
  │                       └── storeMessage() → message loop → SessionQueue → Container
  │
  └── WS: /api/devbox/ws (upgrade)
        └── Envoy validates JWT on upgrade request
              └── WebChannel maintains connection
                    ├── Client→Server: { type: "message", conversationId, content }
                    │     └── same path as REST
                    └── Server→Client: { type: "output"|"status"|"error", conversationId, ... }
                          └── WebChannel.sendMessage() / setTyping()
```

The REST and WS message paths converge at `onMessage()`, entering the same Controller message loop as Telegram/Slack messages.

### Authentication

devbox-agent does **not** validate JWTs. The Envoy proxy handles all authentication:

1. Envoy receives request with `Authorization: Bearer <jwt>`
2. Envoy validates against user-service JWKS (`/auth/.well-known/jwks.json`)
3. Envoy Lua script extracts `sub` claim, sets `X-User-Id` header
4. devbox-agent reads `X-User-Id` from request headers — this is the trusted identity

The `/api/devbox/health` endpoint is added to Envoy's public path whitelist (no JWT required).

---

## API Design

### REST Endpoints

All endpoints prefixed with `/api/devbox`. User identity from `X-User-Id` header.

#### `POST /api/devbox/conversations`

Create a new conversation.

Request body:
```json
{ "agentName": "main" }
```
`agentName` is optional; defaults to the first agent bound to `web:*`.

Response `201`:
```json
{ "conversationId": "uuid-v4" }
```

#### `GET /api/devbox/conversations`

List conversations for the authenticated user.

Response `200`:
```json
{
  "conversations": [
    { "conversationId": "...", "agentName": "main", "createdAt": "...", "lastActivity": "..." }
  ]
}
```

Queries SQLite `sessions` table filtered by `channelId = "web:{userId}"`.

#### `POST /api/devbox/conversations/:id/messages`

Send a message to a conversation.

Request body:
```json
{ "content": "Fix the login bug" }
```

Response `202`:
```json
{ "queued": true }
```

If the conversation's session does not exist yet (first message), it is created on the fly via the normal session initialization path.

#### `GET /api/devbox/conversations/:id/messages`

Fetch message history for a conversation.

Query params: `?before=<timestamp>&limit=50`

Response `200`:
```json
{
  "messages": [
    { "id": "...", "sender": "user|agent", "content": "...", "timestamp": "..." }
  ]
}
```

#### `DELETE /api/devbox/conversations/:id`

End a conversation. Equivalent to `/done --force`: calls `cleanupSessionScope()`, removes session directory, clears DB state.

Response `200`:
```json
{ "deleted": true }
```

#### `GET /api/devbox/health`

Health check for K8s probes and Envoy. No authentication required.

Response `200`:
```json
{ "status": "ok" }
```

### WebSocket Protocol

Connection path: `/api/devbox/ws`

Single connection per user, all conversations multiplexed via `conversationId` field.

#### Server → Client

```typescript
// Agent text output
{ type: "output", conversationId: string, content: string }

// Agent status change
{ type: "status", conversationId: string, status: "processing" | "success" | "error" | "idle" }

// Concurrency limit reached (message still queued, not dropped)
{ type: "error", conversationId: string, code: "concurrency_limit",
  message: "System busy, your request is queued (N ahead)" }

// Session expired (GC'd after 6h inactivity)
{ type: "error", conversationId: string, code: "session_expired",
  message: "Conversation expired after inactivity. Please start a new one." }

// Pong response
{ type: "pong" }
```

#### Client → Server

```typescript
// Send message (shortcut for POST /conversations/:id/messages)
{ type: "message", conversationId: string, content: string }

// Heartbeat
{ type: "ping" }
```

### Concurrency Limit Notification

When a message arrives and the session has no active container:

1. Check `queue.getActiveCount() >= MAX_CONCURRENT_CONTAINERS`
2. If true, send `concurrency_limit` error via WS before enqueuing
3. Message is still enqueued normally — the notification is informational only

`SessionQueue` exposes two new read-only getters:
- `getActiveCount(): number`
- `getWaitingCount(): number`

---

## Configuration

### config.yaml additions

```yaml
web:
  enabled: true
  port: 8080
```

`config.ts` adds:

```typescript
const WebSchema = z.object({
  enabled: z.boolean().default(false),
  port: z.number().int().positive().default(8080),
}).optional();
```

Exported constants: `WEB_ENABLED`, `WEB_PORT`.

### Channel binding

```yaml
channels:
  - id: "web:*"
    agents:
      - name: main
        requires_trigger: false
```

The `web:*` wildcard is resolved in `WebChannel` the same way `tg:user:*` works for Telegram DMs: any `web:{userId}` JID matches when no exact JID binding exists.

---

## Deployment

### New K8s resources

**`k8s/base/service.yaml`** — exposes the controller's HTTP port to the cluster:

```yaml
apiVersion: v1
kind: Service
metadata:
  name: devbox-agent
spec:
  ports:
    - name: http
      port: 80
      targetPort: 8080
  selector:
    app: devbox-agent
```

### Deployment changes

**`k8s/base/deployment.yaml`** — add port declaration and health probes:

```yaml
ports:
  - name: http
    containerPort: 8080
livenessProbe:
  httpGet:
    path: /api/devbox/health
    port: 8080
  initialDelaySeconds: 10
readinessProbe:
  httpGet:
    path: /api/devbox/health
    port: 8080
```

### Staging config

**`k8s/overlays/staging/config.staging.yaml`** — add web config and channel:

```yaml
web:
  enabled: true
  port: 8080

channels:
  # existing slack channels unchanged
  - id: "web:*"
    agents:
      - name: main
        requires_trigger: false
```

### Envoy integration (your-infra-repo, separate PR)

- Route: `/api/devbox` → cluster `devbox-agent` with WebSocket upgrade support, 600s timeout
- Cluster: `devbox-agent.devbox-agent-staging.svc.cluster.local:80`
- JWT: `/api/devbox/health` added to public path whitelist; all other paths require JWT (covered by default catch-all)

---

## File Changes

### New files

| File | Description |
|------|-------------|
| `src/channels/web.ts` | WebChannel implementation |
| `src/channels/web.test.ts` | Unit tests |
| `k8s/base/service.yaml` | K8s Service resource |

### Modified files

| File | Change |
|------|--------|
| `src/config.ts` | Add `WebSchema`, export `WEB_ENABLED` / `WEB_PORT` |
| `src/index.ts` | Initialize WebChannel when `WEB_ENABLED`, push to `channels[]` |
| `src/session-queue.ts` | Add `getActiveCount()` / `getWaitingCount()` getters |
| `k8s/base/deployment.yaml` | Add port + health probes |
| `k8s/base/kustomization.yaml` | Add `service.yaml` to resources |
| `k8s/overlays/staging/config.staging.yaml` | Add `web` config + `web:*` channel |
| `package.json` | Add `ws` + `@types/ws` dependencies |

### Unchanged

- `container-runner.ts`, `container-runtime.ts` — container scheduling unchanged
- `session-gc.ts` — GC rules unchanged (web conversations = thread-scoped, 6h TTL)
- `ipc.ts` — IPC mechanism unchanged
- `router.ts` — message formatting unchanged
- `session-control.ts` — `/done` `/reset` logic reused via DELETE endpoint
- `db.ts` — no schema changes; existing tables sufficient
- `container/` — runner container unchanged
- `agents/` — agent definitions unchanged

### New dependency

`ws` (WebSocket library) + `@types/ws` (dev). No framework dependencies added.
