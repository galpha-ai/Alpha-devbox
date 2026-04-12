import { fireEvent, render, screen, waitFor } from '@testing-library/react';
import { describe, expect, it, vi } from 'vitest';

vi.mock('@ai-sdk/react', async () => {
  const React = await import('react');

  return {
    useChat: ({
      id,
      messages: initialMessages = [],
      onFinish,
    }: {
      id?: string;
      messages?: any[];
      onFinish?: (options: {
        message: any;
        messages: any[];
        isAbort: boolean;
        isDisconnect: boolean;
        isError: boolean;
        finishReason?: string;
      }) => void | Promise<void>;
    }) => {
      const [messages, setMessages] = React.useState(initialMessages);
      const [status, setStatus] = React.useState<'submitted' | 'streaming' | 'ready' | 'error'>('ready');

      React.useEffect(() => {
        setMessages(initialMessages);
        setStatus('ready');
      }, [id]);

      const sendMessage = vi.fn(async ({ text }: { text: string }) => {
        const assistantMessage = {
          id: 'stream-a1',
          role: 'assistant',
          metadata: {
            timestamp: '2026-04-11T00:00:01.000Z',
            sender: 'Devbox',
            senderName: 'Devbox',
          },
          parts: [
            {
              type: 'text',
              text: 'hello back',
              state: 'done',
            },
          ],
        };

        setStatus('submitted');
        setMessages((current: any[]) => [
          ...current,
          {
            id: 'local-u1',
            role: 'user',
            parts: [{ type: 'text', text, state: 'done' }],
          },
        ]);

        await Promise.resolve();

        setStatus('streaming');
        setMessages((current: any[]) => [...current, assistantMessage]);
        setStatus('ready');

        await onFinish?.({
          message: assistantMessage,
          messages: [],
          isAbort: false,
          isDisconnect: false,
          isError: false,
          finishReason: 'stop',
        });
      });

      return {
        id: 'mock-chat',
        messages,
        setMessages,
        sendMessage,
        regenerate: vi.fn(),
        stop: vi.fn(),
        resumeStream: vi.fn(),
        addToolResult: vi.fn(),
        addToolOutput: vi.fn(),
        addToolApprovalResponse: vi.fn(),
        status,
        error: undefined,
        clearError: vi.fn(),
      };
    },
  };
});

vi.mock('@galpha-ai/better-markdown/react', () => ({
  MarkdownChartRenderer: ({
    markdown,
    variant,
    interactive,
  }: {
    markdown: string;
    variant?: string;
    interactive?: boolean;
  }) => (
    <div
      data-testid="vendor-markdown"
      data-markdown={markdown}
      data-variant={variant ?? 'default'}
      data-interactive={String(Boolean(interactive))}
    >
      {markdown}
    </div>
  ),
}));

import { MarkdownChartRenderer } from './MarkdownChartRenderer';
import { ThesisWorkspace } from './ThesisWorkspace';
import type { ThesisTransportClient } from './transport';

function createTransportClient(): ThesisTransportClient {
  return {
    chatTransport: {} as ThesisTransportClient['chatTransport'],
    createConversation: vi.fn(async () => ({ conversationId: 'conv-1' })),
    listConversations: vi.fn(async () => ({ conversations: [] })),
    getMessages: vi.fn(async () => ({
      messages: [
        {
          id: 'u1',
          chat_jid: 'web:test-user',
          thread_id: 'conv-1',
          sender: 'test-user',
          sender_name: 'You',
          content: 'hello',
          timestamp: '2026-04-11T00:00:00.000Z',
          is_bot_message: 0,
        },
        {
          id: 'a1',
          chat_jid: 'web:test-user',
          thread_id: 'conv-1',
          sender: 'Devbox',
          sender_name: 'Devbox',
          content: 'hello back',
          timestamp: '2026-04-11T00:00:01.000Z',
          is_bot_message: 1,
        },
      ],
    })),
    deleteConversation: vi.fn(async () => ({ deleted: true as const })),
  };
}

describe('ThesisWorkspace', () => {
  it('delegates markdown rendering to @galpha-ai/better-markdown', () => {
    const { container } = render(
      <MarkdownChartRenderer
        markdown="**Revenue**"
        proseClassName="prose prose-invert"
        variant="compact"
      />,
    );

    expect(container.querySelector('.prose.prose-invert')).not.toBeNull();

    const vendorRenderer = screen.getByTestId('vendor-markdown');
    expect(vendorRenderer).toHaveAttribute('data-markdown', '**Revenue**');
    expect(vendorRenderer).toHaveAttribute('data-variant', 'compact');
    expect(vendorRenderer).toHaveAttribute('data-interactive', 'true');
  });

  it('renders a single assistant reply after stream hydration', async () => {
    const transportClient = createTransportClient();

    render(
      <ThesisWorkspace
        transportClient={transportClient}
        onLogout={() => {}}
        onSessionExpired={() => {}}
      />,
    );

    const textarea = await screen.findByPlaceholderText('Message the agent...');
    fireEvent.change(textarea, { target: { value: 'hello' } });
    fireEvent.click(screen.getByRole('button', { name: 'Send message' }));

    await screen.findByText('hello back');

    await waitFor(() => {
      expect(screen.getAllByText('hello back')).toHaveLength(1);
      expect(
        screen.queryByText('Assistant is working...'),
      ).not.toBeInTheDocument();
    });
  });
});
