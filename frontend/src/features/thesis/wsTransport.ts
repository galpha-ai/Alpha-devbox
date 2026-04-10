const PING_INTERVAL_MS = 30_000;
const RECONNECT_DELAY_MS = 3_000;
const NORMAL_CLOSE_CODE = 1000;

export type DevboxWsOutputMessage = {
  type: "output";
  conversationId: string;
  content: string;
};

export type DevboxWsStatusMessage = {
  type: "status";
  conversationId: string;
  status: "processing" | "success" | "error" | "idle";
};

export type DevboxWsErrorMessage = {
  type: "error";
  conversationId: string;
  code: string;
  message: string;
};

export type DevboxWsPongMessage = {
  type: "pong";
};

export type DevboxWsMessage =
  | DevboxWsOutputMessage
  | DevboxWsStatusMessage
  | DevboxWsErrorMessage
  | DevboxWsPongMessage;

export type DevboxWsListener = (message: DevboxWsMessage) => void;

export interface DevboxWsClient {
  connect(): void;
  disconnect(): void;
  isConnected(): boolean;
  sendMessage(conversationId: string, content: string): void;
  subscribe(listener: DevboxWsListener): () => void;
}

export interface DevboxWsClientOptions {
  baseUrl: string;
  getAccessToken: () => string | null;
}

export function createDevboxWebSocket(
  options: DevboxWsClientOptions,
): DevboxWsClient {
  let ws: WebSocket | null = null;
  let pingInterval: ReturnType<typeof setInterval> | null = null;
  let reconnectTimeout: ReturnType<typeof setTimeout> | null = null;
  let intentionalDisconnect = false;
  const listeners = new Set<DevboxWsListener>();

  function buildWsUrl(): string {
    const base = options.baseUrl.replace(/\/+$/, "");
    const wsBase = base.replace(/^http/, "ws");
    const token = options.getAccessToken();
    return token
      ? `${wsBase}/ws?token=${encodeURIComponent(token)}`
      : `${wsBase}/ws`;
  }

  function dispatch(message: DevboxWsMessage) {
    for (const listener of listeners) {
      listener(message);
    }
  }

  function startPing() {
    stopPing();
    pingInterval = setInterval(() => {
      if (ws?.readyState === WebSocket.OPEN) {
        ws.send(JSON.stringify({ type: "ping" }));
      }
    }, PING_INTERVAL_MS);
  }

  function stopPing() {
    if (pingInterval !== null) {
      clearInterval(pingInterval);
      pingInterval = null;
    }
  }

  function clearReconnectTimeout() {
    if (reconnectTimeout !== null) {
      clearTimeout(reconnectTimeout);
      reconnectTimeout = null;
    }
  }

  function scheduleReconnect() {
    clearReconnectTimeout();
    reconnectTimeout = setTimeout(() => {
      reconnectTimeout = null;
      connect();
    }, RECONNECT_DELAY_MS);
  }

  function connect() {
    intentionalDisconnect = false;
    clearReconnectTimeout();

    if (
      ws &&
      (ws.readyState === WebSocket.OPEN ||
        ws.readyState === WebSocket.CONNECTING)
    ) {
      return;
    }

    const url = buildWsUrl();
    ws = new WebSocket(url);

    ws.onopen = () => {
      startPing();
    };

    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data) as DevboxWsMessage;
        dispatch(data);
      } catch {
        // Ignore malformed messages
      }
    };

    ws.onclose = (event) => {
      stopPing();
      ws = null;

      if (!intentionalDisconnect && event.code !== NORMAL_CLOSE_CODE) {
        scheduleReconnect();
      }
    };

    ws.onerror = () => {
      // onclose will fire after onerror
    };
  }

  function disconnect() {
    intentionalDisconnect = true;
    clearReconnectTimeout();
    stopPing();

    if (ws) {
      ws.close();
      ws = null;
    }
  }

  function isConnected(): boolean {
    return ws?.readyState === WebSocket.OPEN;
  }

  function sendMessage(conversationId: string, content: string) {
    if (!ws || ws.readyState !== WebSocket.OPEN) {
      throw new Error("WebSocket is not connected");
    }

    ws.send(
      JSON.stringify({
        type: "message",
        conversationId,
        content,
      }),
    );
  }

  function subscribe(listener: DevboxWsListener): () => void {
    listeners.add(listener);
    return () => {
      listeners.delete(listener);
    };
  }

  return {
    connect,
    disconnect,
    isConnected,
    sendMessage,
    subscribe,
  };
}
