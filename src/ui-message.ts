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
      metadata: {
        timestamp: projected.metadata.timestamp || message.timestamp,
        sender: projected.metadata.sender || message.sender,
        senderName:
          projected.metadata.senderName ||
          message.sender_name ||
          message.sender,
      },
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

export function getCanonicalTextContent(
  message: Pick<CanonicalChatMessage, 'parts'>,
) {
  return message.parts
    .map((part) => part.text.trim())
    .filter(Boolean)
    .join('\n\n')
    .trim();
}

function parseStoredUiMessage(
  value?: string | null,
): CanonicalChatMessage | null {
  if (!value) return null;

  try {
    const parsed = JSON.parse(value) as unknown;
    return normalizeStoredUiMessage(parsed);
  } catch {
    return null;
  }
}

function normalizeStoredUiMessage(value: unknown): CanonicalChatMessage | null {
  if (
    !value ||
    typeof value !== 'object' ||
    !('role' in value) ||
    !('parts' in value) ||
    !Array.isArray(value.parts) ||
    (value.role !== 'assistant' && value.role !== 'user')
  ) {
    return null;
  }

  const content = normalizeStoredParts(value.parts);
  if (!content.trim()) {
    return null;
  }

  const metadataSource =
    'metadata' in value && value.metadata && typeof value.metadata === 'object'
      ? value.metadata
      : {};

  return {
    id: 'id' in value && typeof value.id === 'string' ? value.id : '',
    role: value.role,
    parts: [{ type: 'text', text: content, state: 'done' }],
    metadata: {
      timestamp:
        'timestamp' in metadataSource &&
        typeof metadataSource.timestamp === 'string'
          ? metadataSource.timestamp
          : '',
      sender:
        'sender' in metadataSource && typeof metadataSource.sender === 'string'
          ? metadataSource.sender
          : '',
      senderName:
        'senderName' in metadataSource &&
        typeof metadataSource.senderName === 'string'
          ? metadataSource.senderName
          : '',
    },
  };
}

function normalizeStoredParts(parts: unknown[]) {
  return parts
    .map((part) => normalizeStoredPart(part))
    .filter(Boolean)
    .join('\n\n')
    .trim();
}

function normalizeStoredPart(part: unknown) {
  if (!part || typeof part !== 'object' || !('type' in part)) {
    return '';
  }

  if (part.type === 'text' && 'text' in part && typeof part.text === 'string') {
    return part.text;
  }

  if (part.type === 'data-chart_v1' && 'data' in part) {
    return `<<<CHART_V1>>>\n${stringifyStructuredPartData(part.data)}\n<<<END_CHART_V1>>>`;
  }

  if (part.type === 'data-thesis_report_v1' && 'data' in part) {
    return `<<<THESIS_REPORT_V1>>>\n${stringifyStructuredPartData(part.data)}\n<<<END_THESIS_REPORT_V1>>>`;
  }

  if (part.type === 'data-artifact' && 'data' in part) {
    return normalizeLegacyArtifact(part.data);
  }

  return '';
}

function normalizeLegacyArtifact(data: unknown) {
  if (
    !data ||
    typeof data !== 'object' ||
    !('kind' in data) ||
    !('payload' in data)
  ) {
    return '';
  }

  if (data.kind === 'chart') {
    return `<<<CHART_V1>>>\n${stringifyStructuredPartData(data.payload)}\n<<<END_CHART_V1>>>`;
  }

  if (data.kind === 'report') {
    return `<<<THESIS_REPORT_V1>>>\n${stringifyStructuredPartData(data.payload)}\n<<<END_THESIS_REPORT_V1>>>`;
  }

  return '';
}

function stringifyStructuredPartData(data: unknown) {
  return JSON.stringify(data ?? null)
    .replace(/</g, '\\u003c')
    .replace(/>/g, '\\u003e');
}
