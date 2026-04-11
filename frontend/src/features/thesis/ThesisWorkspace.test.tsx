import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";

import { ThesisWorkspace } from "./ThesisWorkspace";
import type { ThesisTransportClient } from "./transport";

function createTransportClient(): ThesisTransportClient {
  let pollCount = 0;

  return {
    createConversation: vi.fn(async () => ({ conversationId: "conv-1" })),
    listConversations: vi.fn(async () => ({ conversations: [] })),
    sendMessage: vi.fn(async () => ({ queued: true as const })),
    getMessages: vi.fn(async () => {
      pollCount += 1;

      if (pollCount === 1) {
        return {
          messages: [
            {
              id: "u1",
              chat_jid: "web:test-user",
              thread_id: "conv-1",
              sender: "test-user",
              sender_name: "You",
              content: "hello",
              timestamp: "2026-04-11T00:00:00.000Z",
              is_bot_message: 0,
            },
          ],
        };
      }

      return {
        messages: [
          {
            id: "u1",
            chat_jid: "web:test-user",
            thread_id: "conv-1",
            sender: "test-user",
            sender_name: "You",
            content: "hello",
            timestamp: "2026-04-11T00:00:00.000Z",
            is_bot_message: 0,
          },
          {
            id: "a1",
            chat_jid: "web:test-user",
            thread_id: "conv-1",
            sender: "Devbox",
            sender_name: "Devbox",
            content: "hello back",
            timestamp: "2026-04-11T00:00:01.000Z",
            is_bot_message: 1,
          },
        ],
      };
    }),
    deleteConversation: vi.fn(async () => ({ deleted: true as const })),
  };
}

describe("ThesisWorkspace", () => {
  it("renders a single assistant reply from backend snapshot polling", async () => {
    const transportClient = createTransportClient();

    render(
      <ThesisWorkspace
        transportClient={transportClient}
        onLogout={() => {}}
        onSessionExpired={() => {}}
      />,
    );

    const textarea = await screen.findByPlaceholderText("Message the agent...");
    fireEvent.change(textarea, { target: { value: "hello" } });
    fireEvent.click(screen.getByRole("button", { name: "Send message" }));

    await screen.findByText("hello back");

    await waitFor(() => {
      expect(screen.getAllByText("hello back")).toHaveLength(1);
      expect(screen.queryByText("Assistant is working...")).not.toBeInTheDocument();
    });
  });
});
