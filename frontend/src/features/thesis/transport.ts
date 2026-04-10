export interface ThesisConversationSummary {
  conversationId: string;
  agentName?: string;
  title: string;
  updatedAt: string;
}

export interface ThesisTransportMessageList<TMessage = unknown> {
  messages: TMessage[];
}

export interface ThesisQueuedResponse {
  queued: true;
  code?: string;
  message?: string;
}

export interface ThesisTransportClientOptions {
  authFetch: (input: string, init?: RequestInit) => Promise<Response>;
}

export type ThesisPromptMode = "chat" | "artifact";

export interface ThesisTransportClient {
  createConversation(): Promise<{ conversationId: string }>;
  listConversations(): Promise<{ conversations: ThesisConversationSummary[] }>;
  sendMessage(conversationId: string, content: string): Promise<ThesisQueuedResponse>;
  getMessages<TMessage = unknown>(
    conversationId: string,
    before?: string,
    limit?: number,
  ): Promise<ThesisTransportMessageList<TMessage>>;
  deleteConversation(conversationId: string): Promise<{ deleted: true }>;
}

export class ThesisTransportError extends Error {
  code?: string;
  status: number;

  constructor(message: string, status: number, code?: string) {
    super(message);
    this.name = "ThesisTransportError";
    this.code = code;
    this.status = status;
  }
}

const CHART_ARTIFACT_PREAMBLE = [
  "CHART_V1",
  "Return the final artifact as exactly one JSON block wrapped by:",
  "<<<CHART_V1>>>",
  "{ ...json... }",
  "<<<END_CHART_V1>>>",
  "You may emit at most one short progress sentence before the wrapped JSON.",
  "After <<<END_CHART_V1>>> emit nothing else.",
  "Required schema: chart_v1.",
  "Required top-level fields: schema, title, summary_markdown, renderer, kind, series, insights.",
  'Supported renderer/kind combinations are renderer: "lightweight" with kind: "line" | "area" | "candlestick", and renderer: "recharts" with kind: "bar".',
  'For lightweight line and area charts, series must look like [{"name":"BTC","data":[{"time":"2026-04-01","value":82450}]}].',
  'For lightweight candlestick charts, series must look like [{"name":"BTC","data":[{"time":"2026-04-01","open":82000,"high":84000,"low":81000,"close":83600}]}].',
  'For recharts bar charts, series must look like [{"name":"Scenarios","data":[{"label":"Base","value":62}]}].',
  "Do not emit arbitrary component names, style tokens, plugins, HTML, or code fences around the JSON.",
  "Keep arrays bounded and compact.",
  "If a chart is not genuinely useful, answer in normal chat instead of forcing an artifact.",
].join("\n");

export function buildArtifactPrompt(userPrompt: string, mode: ThesisPromptMode = "chat") {
  const prompt = userPrompt.trim();
  if (mode === "chat") {
    return prompt;
  }

  return `${CHART_ARTIFACT_PREAMBLE}\n\nUser request:\n${prompt}`;
}

export const buildThesisPrompt = buildArtifactPrompt;

export function createThesisTransportClient(options: ThesisTransportClientOptions): ThesisTransportClient {
  const { authFetch } = options;

  return {
    async createConversation(): Promise<{ conversationId: string }> {
      return requestJson(authFetch, "/api/devbox/conversations", {
        method: "POST",
        body: JSON.stringify({}),
      });
    },

    async listConversations(): Promise<{ conversations: ThesisConversationSummary[] }> {
      return requestJson(authFetch, "/api/devbox/conversations", {
        method: "GET",
      });
    },

    async sendMessage(conversationId: string, content: string): Promise<ThesisQueuedResponse> {
      return requestJson(authFetch, `/api/devbox/conversations/${conversationId}/messages`, {
        method: "POST",
        body: JSON.stringify({ content }),
      });
    },

    async getMessages<TMessage = unknown>(
      conversationId: string,
      before?: string,
      limit = 50,
    ): Promise<ThesisTransportMessageList<TMessage>> {
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
  authFetch: ThesisTransportClientOptions["authFetch"],
  input: string,
  init: RequestInit,
): Promise<T> {
  const response = await authFetch(input, init);
  const payload = await parseJson<T & { error?: string; code?: string; message?: string }>(response);

  if (!response.ok) {
    throw new ThesisTransportError(
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
