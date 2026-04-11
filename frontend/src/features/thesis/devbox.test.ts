import { describe, expect, it } from "vitest";

import { buildConversationSnapshot } from "./devbox";

describe("buildConversationSnapshot", () => {
  it("collapses adjacent duplicate assistant replies", () => {
    const snapshot = buildConversationSnapshot([
      {
        id: "u1",
        chat_jid: "web:user1",
        thread_id: "conv-1",
        sender: "user1",
        sender_name: "User 1",
        content: "hello",
        timestamp: "2026-04-11T00:00:00.000Z",
        is_bot_message: 0,
      },
      {
        id: "a1",
        chat_jid: "web:user1",
        thread_id: "conv-1",
        sender: "Devbox",
        sender_name: "Devbox",
        content: "same reply",
        timestamp: "2026-04-11T00:00:01.000Z",
        is_bot_message: 1,
      },
      {
        id: "a2",
        chat_jid: "web:user1",
        thread_id: "conv-1",
        sender: "Devbox",
        sender_name: "Devbox",
        content: "same reply",
        timestamp: "2026-04-11T00:00:02.000Z",
        is_bot_message: 1,
      },
    ]);

    expect(snapshot.messages).toHaveLength(2);
    expect(snapshot.messages[1].content).toBe("same reply");
    expect(snapshot.assistantTranscript).toBe("same reply");
  });
});
