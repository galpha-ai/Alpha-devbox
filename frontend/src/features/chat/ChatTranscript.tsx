import type { MutableRefObject } from 'react';
import { Sparkles } from 'lucide-react';

import { MarkdownChartRenderer } from './MarkdownChartRenderer';
import { getChatMessageText, type ChatTranscriptMessage } from './chat-message';

const proseClasses = `prose prose-invert prose-sm max-w-none 
  prose-headings:text-foreground prose-headings:font-display
  prose-h2:text-lg prose-h3:text-base
  prose-p:text-[hsl(var(--body-foreground))] prose-p:leading-relaxed
  prose-li:text-[hsl(var(--body-muted))] prose-li:leading-relaxed
  prose-strong:text-foreground prose-code:text-foreground`;

export function ChatTranscript({
  messages,
  highlightedMessageId,
  messageRefMap,
}: {
  messages: ChatTranscriptMessage[];
  highlightedMessageId?: string | null;
  messageRefMap?: MutableRefObject<Record<string, HTMLElement | null>>;
}) {
  return (
    <section className="space-y-4">
      {messages.map((message) => (
        <MessageBubble
          key={message.id}
          message={message}
          highlighted={highlightedMessageId === message.id}
          messageRefMap={messageRefMap}
        />
      ))}
    </section>
  );
}

function MessageBubble({
  message,
  highlighted = false,
  messageRefMap,
}: {
  message: ChatTranscriptMessage;
  highlighted?: boolean;
  messageRefMap?: MutableRefObject<Record<string, HTMLElement | null>>;
}) {
  const content = getChatMessageText(message).trim();

  const setRef = (node: HTMLElement | null) => {
    if (messageRefMap) {
      messageRefMap.current[message.id] = node;
    }
  };

  if (message.role === 'user') {
    return (
      <div
        ref={setRef}
        data-testid={`replay-message-${message.id}`}
        data-highlighted={highlighted ? 'true' : 'false'}
        tabIndex={-1}
        className="flex justify-end rounded-2xl outline-none transition"
      >
        <div
          className={[
            'min-w-0 max-w-[85%] whitespace-pre-wrap break-words rounded-2xl rounded-br-md bg-muted/60 px-4 py-3 text-sm leading-relaxed text-foreground [overflow-wrap:anywhere] transition',
            highlighted
              ? 'bg-muted/80 shadow-[inset_0_0_0_1px_rgba(193,255,0,0.22)]'
              : '',
          ].join(' ')}
        >
          {content}
        </div>
      </div>
    );
  }

  return (
    <div
      ref={setRef}
      data-testid={`replay-message-${message.id}`}
      data-highlighted={highlighted ? 'true' : 'false'}
      tabIndex={-1}
      className="flex items-start gap-3 rounded-2xl outline-none transition"
    >
      <div className="mt-1 flex h-8 w-8 items-center justify-center rounded-full border border-border/30 bg-card/70">
        <Sparkles className="h-4 w-4 text-primary" />
      </div>
      <div className="min-w-0 max-w-[85%] space-y-3">
        {content ? (
          <div
            className={[
              'min-w-0 overflow-hidden rounded-2xl rounded-bl-md border border-border/30 bg-card/70 px-4 py-3 transition',
              highlighted
                ? 'shadow-[inset_0_0_0_1px_rgba(193,255,0,0.22)]'
                : '',
            ].join(' ')}
          >
            <MarkdownChartRenderer
              markdown={content}
              proseClassName={proseClasses}
            />
          </div>
        ) : null}
      </div>
    </div>
  );
}
