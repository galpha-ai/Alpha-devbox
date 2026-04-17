import type { UIMessage } from 'ai';

export type ChatTranscriptMessage = UIMessage<{
  timestamp?: string;
  sender?: string;
  senderName?: string;
}>;

export function getChatMessageText(message: ChatTranscriptMessage) {
  return message.parts
    .filter(
      (part): part is Extract<typeof part, { type: 'text' }> =>
        part.type === 'text',
    )
    .map((part) => part.text)
    .join('\n\n');
}
