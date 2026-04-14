import { DefaultChatTransport, type UIMessage } from "ai";

export interface ChatConversationSummary {
  conversationId: string;
  agentName?: string;
  title: string;
  updatedAt: string;
}

export interface ChatTransportMessageList<TMessage = unknown> {
  messages: TMessage[];
}

export interface ChatTransportClientOptions {
  authFetch: (input: string, init?: RequestInit) => Promise<Response>;
}

export interface ChatTransportClient {
  chatTransport: DefaultChatTransport<UIMessage>;
  createConversation(): Promise<{ conversationId: string }>;
  listConversations(): Promise<{ conversations: ChatConversationSummary[] }>;
  getUiMessages<TMessage extends UIMessage = UIMessage>(
    conversationId: string,
    limit?: number,
  ): Promise<ChatTransportMessageList<TMessage>>;
  getMessages<TMessage = unknown>(
    conversationId: string,
    before?: string,
    limit?: number,
  ): Promise<ChatTransportMessageList<TMessage>>;
  deleteConversation(conversationId: string): Promise<{ deleted: true }>;
}

export class ChatTransportError extends Error {
  code?: string;
  status: number;

  constructor(message: string, status: number, code?: string) {
    super(message);
    this.name = "ChatTransportError";
    this.code = code;
    this.status = status;
  }
}

export function createChatTransportClient(options: ChatTransportClientOptions): ChatTransportClient {
  const { authFetch } = options;
  const chatTransport = new DefaultChatTransport<UIMessage>({
    api: "/api/devbox/chat",
    fetch: (input, init) => authFetch(resolveTransportInput(input), init),
  });

  return {
    chatTransport,

    async createConversation(): Promise<{ conversationId: string }> {
      return requestJson(authFetch, "/api/devbox/conversations", {
        method: "POST",
        body: JSON.stringify({}),
      });
    },

    async listConversations(): Promise<{ conversations: ChatConversationSummary[] }> {
      return requestJson(authFetch, "/api/devbox/conversations", {
        method: "GET",
      });
    },

    async getUiMessages<TMessage extends UIMessage = UIMessage>(
      conversationId: string,
      limit = 100,
    ): Promise<ChatTransportMessageList<TMessage>> {
      const params = new URLSearchParams();
      params.set("limit", String(limit));

      return requestJson(
        authFetch,
        `/api/devbox/conversations/${conversationId}/ui-messages?${params.toString()}`,
        {
          method: "GET",
        },
      );
    },

    async getMessages<TMessage = unknown>(
      conversationId: string,
      before?: string,
      limit = 50,
    ): Promise<ChatTransportMessageList<TMessage>> {
      const params = new URLSearchParams();
      if (before) {
        params.set("before", before);
      }
      params.set("limit", String(limit));

      const query = params.toString();
      return requestJson(authFetch, `/api/devbox/conversations/${conversationId}/messages?${query}`, {
        method: "GET",
      });
    },

    async deleteConversation(conversationId: string): Promise<{ deleted: true }> {
      return requestJson(authFetch, `/api/devbox/conversations/${conversationId}`, {
        method: "DELETE",
      });
    },
  };
}

async function requestJson<T>(
  authFetch: ChatTransportClientOptions["authFetch"],
  input: string,
  init: RequestInit,
): Promise<T> {
  const response = await authFetch(input, init);
  const payload = await parseJson<T & { error?: string; code?: string; message?: string }>(response);

  if (!response.ok) {
    throw new ChatTransportError(
      payload?.message || payload?.error || `Request failed (${response.status})`,
      response.status,
      payload?.code,
    );
  }

  return payload as T;
}

async function parseJson<T>(response: Response) {
  try {
    return await response.json() as T;
  } catch {
    return null;
  }
}

function resolveTransportInput(input: RequestInfo | URL) {
  if (typeof input === "string") {
    return input;
  }

  if (input instanceof URL) {
    return input.toString();
  }

  return input.url;
}
