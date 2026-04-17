import { describe, expect, it, vi } from "vitest";
import type { UIMessage } from "ai";

import {
  ChatTransportError,
  createChatTransportClient,
  createReplayTransportClient,
} from "./transport";

describe("createReplayTransportClient", () => {
  it("loads canonical UI messages from the replay endpoint", async () => {
    const fetchMock = vi.fn<typeof fetch>().mockResolvedValue(
      new Response(
        JSON.stringify({
          messages: [
            {
              id: "assistant-1",
              role: "assistant",
              parts: [{ type: "text", text: "hello", state: "done" }],
            },
          ],
        }),
        {
          status: 200,
          headers: { "Content-Type": "application/json" },
        },
      ),
    );

    const client = createReplayTransportClient({ fetch: fetchMock });
    const response = await client.getReplayUiMessages("rpl_123");

    expect(fetchMock).toHaveBeenCalledWith(
      "/api/devbox/replays/rpl_123/ui-messages",
      expect.objectContaining({ method: "GET" }),
    );
    expect(response.messages).toHaveLength(1);
  });

  it("throws ChatTransportError for replay API failures", async () => {
    const fetchMock = vi.fn<typeof fetch>().mockResolvedValue(
      new Response(
        JSON.stringify({ message: "Replay missing", code: "replay_not_found" }),
        {
          status: 404,
          headers: { "Content-Type": "application/json" },
        },
      ),
    );

    const client = createReplayTransportClient({ fetch: fetchMock });

    await expect(client.getReplayUiMessages("missing")).rejects.toEqual(
      expect.objectContaining<Partial<ChatTransportError>>({
        name: "ChatTransportError",
        status: 404,
        code: "replay_not_found",
        message: "Replay missing",
      }),
    );
  });
});

describe("createChatTransportClient", () => {
  it("sends only the last message in the chat transport request body", async () => {
    const authFetch = vi.fn<typeof fetch>().mockResolvedValue(
      new Response("", {
        status: 200,
        headers: { "Content-Type": "text/event-stream" },
      }),
    );

    const client = createChatTransportClient({ authFetch });
    const firstMessage: UIMessage = {
      id: "u1",
      role: "user",
      parts: [{ type: "text", text: "first", state: "done" }],
    };
    const secondMessage: UIMessage = {
      id: "u2",
      role: "user",
      parts: [{ type: "text", text: "second", state: "done" }],
    };

    // call the transport directly to verify body shaping
    await client.chatTransport.sendMessages({
      chatId: "conv-1",
      messages: [firstMessage, secondMessage],
      trigger: "submit-message",
      messageId: "u2",
      abortSignal: new AbortController().signal,
    });

    expect(authFetch).toHaveBeenCalledWith(
      "/api/devbox/chat",
      expect.objectContaining({
        method: "POST",
        body: JSON.stringify({
          id: "conv-1",
          trigger: "submit-message",
          messageId: "u2",
          message: {
            id: "u2",
            role: "user",
            parts: [{ type: "text", text: "second", state: "done" }],
          },
        }),
      }),
    );
  });
});
