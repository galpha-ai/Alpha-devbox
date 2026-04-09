# Devbox Web Channel API Reference

Base URL: `https://your-domain.example.com/api/devbox`

## Authentication

All endpoints except `/health` require a valid JWT token issued by `your-auth-service`.

```
Authorization: Bearer <jwt-token>
```

Envoy validates the JWT and injects `X-User-Id` header from the `sub` claim. The devbox-agent service reads `X-User-Id` directly — it never touches the JWT itself.

---

## REST Endpoints

### Health Check

```
GET /api/devbox/health
```

No authentication required.

**Response** `200`

```json
{ "status": "ok" }
```

---

### Create Conversation

```
POST /api/devbox/conversations
```

Creates a new conversation and returns its ID. The conversation is not activated until the first message is sent.

**Request body** (optional)

```json
{}
```

**Response** `201`

```json
{
  "conversationId": "550e8400-e29b-41d4-a716-446655440000"
}
```

---

### List Conversations

```
GET /api/devbox/conversations
```

Returns all conversations for the authenticated user that have an active session (not yet GC'd).

**Response** `200`

```json
{
  "conversations": [
    { "conversationId": "550e8400-...", "agentName": "devbox-dev" },
    { "conversationId": "7c9e6679-...", "agentName": "devbox-dev" }
  ]
}
```

Note: Thread-scoped sessions are garbage collected after 6 hours of inactivity. Conversations that have been GC'd will not appear in this list.

---

### Send Message

```
POST /api/devbox/conversations/:conversationId/messages
```

Sends a message to the agent. The message is queued for processing and the agent will respond asynchronously via WebSocket.

**Path parameters**

| Parameter | Description |
|-----------|-------------|
| `conversationId` | UUID from Create Conversation, or any client-generated UUID |

**Request body**

```json
{
  "content": "Fix the login bug in auth.ts"
}
```

**Response** `202`

```json
{ "queued": true }
```

**Error** `400` — missing or non-string `content`

```json
{ "error": "content is required" }
```

If the system is at the global concurrency limit, the message is still queued but a `concurrency_limit` notification is sent via WebSocket (see below).

---

### Get Message History

```
GET /api/devbox/conversations/:conversationId/messages
```

Returns messages in reverse chronological order (newest first).

**Path parameters**

| Parameter | Description |
|-----------|-------------|
| `conversationId` | Conversation UUID |

**Query parameters**

| Parameter | Default | Description |
|-----------|---------|-------------|
| `before` | — | ISO 8601 timestamp cursor. Only returns messages before this time. |
| `limit` | `50` | Maximum number of messages to return. |

**Response** `200`

```json
{
  "messages": [
    {
      "id": "web-1712448000000-a1b2",
      "chat_jid": "web:user123",
      "thread_id": "550e8400-...",
      "sender": "user123",
      "sender_name": "user123",
      "content": "Fix the login bug",
      "timestamp": "2026-04-07T00:00:00.000Z",
      "is_bot_message": 0
    }
  ]
}
```

Pagination: use the `timestamp` of the last message as the `before` parameter for the next page.

---

### Delete Conversation

```
DELETE /api/devbox/conversations/:conversationId
```

Ends the conversation and cleans up the session workspace. Equivalent to the `/done --force` command. Stops any running container, removes the session directory, and clears DB state.

**Response** `200`

```json
{ "deleted": true }
```

---

## WebSocket

### Connection

```
wss://your-domain.example.com/api/devbox/ws
```

Requires JWT in the upgrade request (Envoy validates it and injects `X-User-Id`). One connection per user; all conversations are multiplexed via the `conversationId` field.

### Client → Server Messages

#### Send Message

```json
{
  "type": "message",
  "conversationId": "550e8400-...",
  "content": "Fix the login bug"
}
```

Equivalent to `POST /conversations/:id/messages`. Both paths can be used interchangeably.

#### Ping

```json
{ "type": "ping" }
```

### Server → Client Messages

#### Agent Output

Sent when the agent produces text output.

```json
{
  "type": "output",
  "conversationId": "550e8400-...",
  "content": "I found the bug in auth.ts line 42..."
}
```

#### Status Change

Sent when the agent's processing status changes.

```json
{
  "type": "status",
  "conversationId": "550e8400-...",
  "status": "processing"
}
```

| Status | Meaning |
|--------|---------|
| `processing` | Agent is working on the request |
| `success` | Agent completed successfully |
| `error` | Agent encountered an error |
| `idle` | No active work |

#### Concurrency Limit

Sent when a message is queued because all container slots are occupied. The message is **not dropped** — it will be processed when a slot becomes available.

```json
{
  "type": "error",
  "conversationId": "550e8400-...",
  "code": "concurrency_limit",
  "message": "System busy, your request is queued (3 ahead)"
}
```

#### Session Expired

Sent when a message targets a conversation whose session was garbage collected (6h inactivity).

```json
{
  "type": "error",
  "conversationId": "550e8400-...",
  "code": "session_expired",
  "message": "Conversation expired after inactivity. Please start a new one."
}
```

#### Pong

Response to client ping.

```json
{ "type": "pong" }
```

---

## Error Responses

All REST endpoints return JSON error bodies:

| Status | Meaning |
|--------|---------|
| `400` | Invalid request body or missing required fields |
| `401` | Missing authentication (no JWT / no `X-User-Id` header) |
| `404` | Unknown endpoint |

```json
{ "error": "description of the error" }
```

---

## Deployment

| Environment | Base URL |
|-------------|----------|
| Development | `https://localhost:8080/api/devbox` |
| Staging | `https://your-domain.example.com/api/devbox` |

Traffic flow: `Client → GCE Ingress → Envoy (JWT + X-User-Id injection) → devbox-agent Service → Pod`
