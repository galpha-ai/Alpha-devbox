export type CanonicalChatMessage = {
  id: string;
  role: 'user' | 'assistant';
  parts: Array<{ type: 'text'; text: string; state: 'done' }>;
  metadata: {
    timestamp: string;
    sender: string;
    senderName: string;
  };
};

type StoredMessageLike = {
  id: string;
  sender: string;
  sender_name: string;
  content: string;
  timestamp: string;
  is_bot_message?: boolean;
  ui_message_json?: string | null;
};

export function buildCanonicalChatMessage(
  message: StoredMessageLike,
): CanonicalChatMessage {
  const projected = parseStoredUiMessage(message.ui_message_json);
  if (projected) {
    return {
      ...projected,
      id: projected.id || message.id,
    };
  }

  return {
    id: message.id,
    role: message.is_bot_message ? 'assistant' : 'user',
    parts: [
      {
        type: 'text',
        text: message.content,
        state: 'done',
      },
    ],
    metadata: {
      timestamp: message.timestamp,
      sender: message.sender,
      senderName: message.sender_name || message.sender,
    },
  };
}

export function buildAssistantUiMessageProjection(input: {
  id: string;
  content: string;
  timestamp: string;
  sender: string;
  senderName: string;
}): CanonicalChatMessage {
  return {
    id: input.id,
    role: 'assistant',
    parts: [
      {
        type: 'text',
        text: input.content,
        state: 'done',
      },
    ],
    metadata: {
      timestamp: input.timestamp,
      sender: input.sender,
      senderName: input.senderName,
    },
  };
}

export function stringifyUiMessageProjection(message: CanonicalChatMessage) {
  return JSON.stringify(message);
}

function parseStoredUiMessage(
  value?: string | null,
): CanonicalChatMessage | null {
  if (!value) return null;

  try {
    const parsed = JSON.parse(value) as CanonicalChatMessage;
    if (
      !parsed ||
      typeof parsed !== 'object' ||
      (parsed.role !== 'assistant' && parsed.role !== 'user') ||
      !Array.isArray(parsed.parts)
    ) {
      return null;
    }
    return parsed;
  } catch {
    return null;
  }
}
