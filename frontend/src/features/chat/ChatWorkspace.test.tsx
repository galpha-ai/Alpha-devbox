/* eslint-disable @typescript-eslint/no-explicit-any, react-hooks/exhaustive-deps */
import { fireEvent, render, screen, waitFor } from '@testing-library/react';
import { useState } from 'react';
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
      const messageCounterRef = React.useRef(0);

      React.useEffect(() => {
        setMessages(initialMessages);
        setStatus('ready');
        messageCounterRef.current = 0;
      }, [id]);

      const sendMessage = vi.fn(async ({ text }: { text: string }) => {
        const seq = ++messageCounterRef.current;
        const userMessage = {
          id: `local-u${seq}`,
          role: 'user',
          parts: [{ type: 'text', text, state: 'done' }],
        };
        const shouldStreamEmptyAssistant = text.includes('__EMPTY_ASSISTANT__');
        const assistantMessage = {
          id: `stream-a${seq}`,
          role: 'assistant',
          metadata: {
            timestamp: `2026-04-11T00:00:${String(seq).padStart(2, '0')}.000Z`,
            sender: 'Devbox',
            senderName: 'Devbox',
          },
          parts: shouldStreamEmptyAssistant
            ? []
            : [
                {
                  type: 'text',
                  text: 'hello back',
                  state: 'done',
                },
              ],
        };

        let messagesAfterUser: any[] = [];
        let messagesAfterAssistant: any[] = [];

        setStatus('submitted');
        setMessages((current: any[]) => {
          messagesAfterUser = [...current, userMessage];
          return messagesAfterUser;
        });

        await Promise.resolve();

        setStatus('streaming');
        setMessages((current: any[]) => {
          messagesAfterAssistant = [...current, assistantMessage];
          return messagesAfterAssistant;
        });
        setStatus('ready');
        await Promise.resolve();

        await onFinish?.({
          message: assistantMessage,
          messages:
            messagesAfterAssistant.length > 0
              ? messagesAfterAssistant
              : [...messagesAfterUser, assistantMessage],
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
import { ChatWorkspace } from './ChatWorkspace';
import type { ChatTransportClient } from './transport';

function createTransportClient(): ChatTransportClient {
  return {
    chatTransport: {} as ChatTransportClient['chatTransport'],
    createConversation: vi.fn(async () => ({ conversationId: 'conv-1' })),
    listConversations: vi.fn(async () => ({ conversations: [] })),
    getUiMessages: vi.fn(async () => ({
      messages: [
        {
          id: 'u1',
          role: 'user',
          metadata: {
            timestamp: '2026-04-11T00:00:00.000Z',
            sender: 'test-user',
            senderName: 'You',
          },
          parts: [{ type: 'text', text: 'hello', state: 'done' }],
        },
        {
          id: 'a1',
          role: 'assistant',
          metadata: {
            timestamp: '2026-04-11T00:00:01.000Z',
            sender: 'Devbox',
            senderName: 'Devbox',
          },
          parts: [{ type: 'text', text: 'hello back', state: 'done' }],
        },
      ],
    })),
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

function createApiMessage(
  id: string,
  role: 'user' | 'assistant',
  content: string,
  timestamp: string,
  conversationId = 'conv-1',
) {
  return {
    id,
    chat_jid: 'web:test-user',
    thread_id: conversationId,
    sender: role === 'user' ? 'test-user' : 'Devbox',
    sender_name: role === 'user' ? 'You' : 'Devbox',
    content,
    timestamp,
    is_bot_message: role === 'assistant' ? 1 : 0,
  };
}

function createUiMessage(
  id: string,
  role: 'user' | 'assistant',
  content: string,
  timestamp: string,
) {
  return {
    id,
    role,
    metadata: {
      timestamp,
      sender: role === 'user' ? 'test-user' : 'Devbox',
      senderName: role === 'user' ? 'You' : 'Devbox',
    },
    parts: content
      ? [{ type: 'text', text: content, state: 'done' as const }]
      : [],
  };
}

function deferred<T>() {
  let resolve!: (value: T) => void;
  const promise = new Promise<T>((res) => {
    resolve = res;
  });

  return { promise, resolve };
}

describe('ChatWorkspace', () => {
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
      <ChatWorkspace
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

  it('rehydrates canonical history when the streamed finish payload has no assistant text', async () => {
    const transportClient = createTransportClient();
    vi.mocked(transportClient.getUiMessages).mockResolvedValueOnce({
      messages: [
        createUiMessage(
          'u1',
          'user',
          '__EMPTY_ASSISTANT__ show canonical answer',
          '2026-04-11T00:00:00.000Z',
        ),
        createUiMessage(
          'a1',
          'assistant',
          'canonical answer',
          '2026-04-11T00:00:01.000Z',
        ),
      ],
    });

    render(
      <ChatWorkspace
        transportClient={transportClient}
        onLogout={() => {}}
        onSessionExpired={() => {}}
      />,
    );

    const textarea = await screen.findByPlaceholderText('Message the agent...');
    fireEvent.change(textarea, {
      target: { value: '__EMPTY_ASSISTANT__ show canonical answer' },
    });
    fireEvent.click(screen.getByRole('button', { name: 'Send message' }));

    await screen.findByText('canonical answer');
    expect(
      screen.queryByText('Generated a structured response.'),
    ).not.toBeInTheDocument();
    expect(transportClient.getUiMessages).toHaveBeenCalledWith('conv-1', 100);
  });

  it('ignores stale hydration results so later follow-ups do not disappear', async () => {
    const hydrate1 = deferred<{ messages: ReturnType<typeof createUiMessage>[] }>();
    const hydrate2 = deferred<{ messages: ReturnType<typeof createUiMessage>[] }>();
    const hydrate3 = deferred<{ messages: ReturnType<typeof createUiMessage>[] }>();

    const transportClient = createTransportClient();
    vi.mocked(transportClient.getUiMessages)
      .mockImplementationOnce(async () => hydrate1.promise)
      .mockImplementationOnce(async () => hydrate2.promise)
      .mockImplementationOnce(async () => hydrate3.promise);

    render(
      <ChatWorkspace
        transportClient={transportClient}
        onLogout={() => {}}
        onSessionExpired={() => {}}
      />,
    );

    const textarea = await screen.findByPlaceholderText('Message the agent...');

    fireEvent.change(textarea, { target: { value: 'Mean reversion on S&P 500 sectors' } });
    fireEvent.click(screen.getByRole('button', { name: 'Send message' }));
    await screen.findByText('hello back');
    await screen.findAllByText('Mean reversion on S&P 500 sectors');

    fireEvent.change(textarea, { target: { value: 'follow up one' } });
    fireEvent.click(screen.getByRole('button', { name: 'Send message' }));
    await screen.findAllByText('follow up one');

    fireEvent.change(textarea, { target: { value: 'follow up two' } });
    fireEvent.click(screen.getByRole('button', { name: 'Send message' }));
    await screen.findAllByText('follow up two');

    hydrate3.resolve({
      messages: [
        createUiMessage('u1', 'user', 'Mean reversion on S&P 500 sectors', '2026-04-11T00:00:00.000Z'),
        createUiMessage('a1', 'assistant', 'hello back', '2026-04-11T00:00:01.000Z'),
        createUiMessage('u2', 'user', 'follow up one', '2026-04-11T00:00:02.000Z'),
        createUiMessage('a2', 'assistant', 'hello back', '2026-04-11T00:00:03.000Z'),
        createUiMessage('u3', 'user', 'follow up two', '2026-04-11T00:00:04.000Z'),
        createUiMessage('a3', 'assistant', 'hello back', '2026-04-11T00:00:05.000Z'),
      ],
    });

    await screen.findAllByText('follow up two');

    hydrate1.resolve({
      messages: [
        createUiMessage('u1', 'user', 'Mean reversion on S&P 500 sectors', '2026-04-11T00:00:00.000Z'),
        createUiMessage('a1', 'assistant', 'hello back', '2026-04-11T00:00:01.000Z'),
      ],
    });
    hydrate2.resolve({
      messages: [
        createUiMessage('u1', 'user', 'Mean reversion on S&P 500 sectors', '2026-04-11T00:00:00.000Z'),
        createUiMessage('a1', 'assistant', 'hello back', '2026-04-11T00:00:01.000Z'),
        createUiMessage('u2', 'user', 'follow up one', '2026-04-11T00:00:02.000Z'),
        createUiMessage('a2', 'assistant', 'hello back', '2026-04-11T00:00:03.000Z'),
      ],
    });

    await waitFor(() => {
      expect(screen.getAllByText('Mean reversion on S&P 500 sectors').length).toBeGreaterThan(0);
      expect(screen.getAllByText('follow up one').length).toBeGreaterThan(0);
      expect(screen.getAllByText('follow up two').length).toBeGreaterThan(0);
    });
  });

  it('hydrates stored follow-ups so existing turns remain visible', async () => {
    const transportClient = createTransportClient();
    vi.mocked(transportClient.listConversations).mockResolvedValueOnce({
      conversations: [
        {
          conversationId: 'conv-hydrated',
          title: 'Mean reversion',
          updatedAt: '2026-04-11T00:00:05.000Z',
        },
      ],
    });

    vi.mocked(transportClient.getUiMessages).mockResolvedValueOnce({
      messages: [
        createUiMessage(
          'u1',
          'user',
          'Mean reversion on S&P 500 sectors',
          '2026-04-11T00:00:00.000Z',
        ),
        createUiMessage(
          'a1',
          'assistant',
          'Cross-sector relative mean reversion works over short windows.',
          '2026-04-11T00:00:01.000Z',
        ),
        createUiMessage(
          'u2',
          'user',
          'follow up one',
          '2026-04-11T00:00:02.000Z',
        ),
        createUiMessage(
          'a2',
          'assistant',
          'First follow-up answer',
          '2026-04-11T00:00:03.000Z',
        ),
        createUiMessage(
          'u3',
          'user',
          'follow up two',
          '2026-04-11T00:00:04.000Z',
        ),
        createUiMessage(
          'a3',
          'assistant',
          'Second follow-up answer',
          '2026-04-11T00:00:05.000Z',
        ),
      ],
    });

    render(
      <ChatWorkspace
        transportClient={transportClient}
        onLogout={() => {}}
        onSessionExpired={() => {}}
      />,
    );

    await waitFor(() => {
      expect(screen.getByText('follow up one')).toBeInTheDocument();
      expect(screen.getByText('follow up two')).toBeInTheDocument();
      expect(screen.getByText('Second follow-up answer')).toBeInTheDocument();
    });
  });

  it('preserves distinct assistant turns even when adjacent hydrated content matches', async () => {
    const transportClient = createTransportClient();
    vi.mocked(transportClient.listConversations).mockResolvedValueOnce({
      conversations: [{ conversationId: 'conv-1', title: 'Test', updatedAt: '2026-04-11T00:00:05.000Z' }],
    });
    vi.mocked(transportClient.getUiMessages).mockResolvedValueOnce({
      messages: [
        createUiMessage('u1', 'user', 'q1', '2026-04-11T00:00:00.000Z'),
        createUiMessage('a1', 'assistant', 'same answer', '2026-04-11T00:00:01.000Z'),
        createUiMessage('u2', 'user', 'q2', '2026-04-11T00:00:02.000Z'),
        createUiMessage('a2', 'assistant', 'same answer', '2026-04-11T00:00:03.000Z'),
      ],
    });

    render(
      <ChatWorkspace
        transportClient={transportClient}
        onLogout={() => {}}
        onSessionExpired={() => {}}
      />,
    );

    await waitFor(() => {
      expect(screen.getByText('q1')).toBeInTheDocument();
      expect(screen.getByText('q2')).toBeInTheDocument();
      expect(screen.getAllByText('same answer')).toHaveLength(2);
    });
  });

  it('keeps the streamed follow-up visible after loading canonical history', async () => {
    const transportClient = createTransportClient();
    vi.mocked(transportClient.listConversations).mockResolvedValueOnce({
      conversations: [
        {
          conversationId: 'conv-identical-stream',
          title: 'BTC SMA',
          updatedAt: '2026-04-12T00:00:04.000Z',
        },
      ],
    });

    const initialHistory = [
      createUiMessage(
        'u1',
        'user',
        'Initial BTC momentum setup?',
        '2026-04-12T00:00:00.000Z',
      ),
      createUiMessage(
        'a1',
        'assistant',
        'Use a 20-day SMA for the base signal.',
        '2026-04-12T00:00:01.000Z',
      ),
    ];

    vi.mocked(transportClient.getUiMessages).mockResolvedValueOnce({
      messages: initialHistory,
    });

    render(
      <ChatWorkspace
        transportClient={transportClient}
        onLogout={() => {}}
        onSessionExpired={() => {}}
      />,
    );

    await screen.findByText('Initial BTC momentum setup?');

    const textarea = await screen.findByPlaceholderText('Message the agent...');
    fireEvent.change(textarea, { target: { value: 'Any risk controls for chop?' } });
    fireEvent.click(screen.getByRole('button', { name: 'Send message' }));

    await waitFor(() => {
      expect(
        screen.getByText('Use a 20-day SMA for the base signal.'),
      ).toBeInTheDocument();
      expect(screen.getByText('hello back')).toBeInTheDocument();
      expect(screen.getAllByText('Any risk controls for chop?').length).toBeGreaterThan(0);
    });
  });

  it('does not use the legacy raw messages endpoint on the main web chat path', async () => {
    const transportClient = createTransportClient();
    vi.mocked(transportClient.listConversations).mockResolvedValueOnce({
      conversations: [
        {
          conversationId: 'conv-ui-only',
          title: 'UI only',
          updatedAt: '2026-04-12T00:00:04.000Z',
        },
      ],
    });

    render(
      <ChatWorkspace
        transportClient={transportClient}
        onLogout={() => {}}
        onSessionExpired={() => {}}
      />,
    );

    await screen.findByText('hello');

    expect(transportClient.getUiMessages).toHaveBeenCalledWith(
      'conv-ui-only',
      100,
    );
    expect(transportClient.getMessages).not.toHaveBeenCalled();
  });

  it('keeps the starter state on the root route even when prior conversations exist', async () => {
    const transportClient = createTransportClient();
    vi.mocked(transportClient.listConversations).mockResolvedValueOnce({
      conversations: [
        {
          conversationId: 'conv-existing',
          title: 'Existing',
          updatedAt: '2026-04-12T00:00:04.000Z',
        },
      ],
    });

    render(
      <ChatWorkspace
        transportClient={transportClient}
        activeConversationId=""
        onActiveConversationIdChange={() => {}}
        onLogout={() => {}}
        onSessionExpired={() => {}}
      />,
    );

    await screen.findByPlaceholderText('Message the agent...');

    expect(screen.queryByText('hello')).not.toBeInTheDocument();
    expect(transportClient.getUiMessages).not.toHaveBeenCalled();
  });

  it('notifies the host when a new conversation id is created', async () => {
    const transportClient = createTransportClient();
    const onActiveConversationIdChange = vi.fn();

    render(
      <ChatWorkspace
        transportClient={transportClient}
        activeConversationId=""
        onActiveConversationIdChange={onActiveConversationIdChange}
        onLogout={() => {}}
        onSessionExpired={() => {}}
      />,
    );

    const textarea = await screen.findByPlaceholderText('Message the agent...');
    fireEvent.change(textarea, { target: { value: 'hello' } });
    fireEvent.click(screen.getByRole('button', { name: 'Send message' }));

    await waitFor(() => {
      expect(onActiveConversationIdChange).toHaveBeenCalledWith('conv-1');
    });
  });

  it('hydrates the route-selected conversation when the host provides an active id', async () => {
    const transportClient = createTransportClient();
    vi.mocked(transportClient.listConversations).mockResolvedValueOnce({
      conversations: [
        {
          conversationId: 'conv-1',
          title: 'First',
          updatedAt: '2026-04-11T00:00:01.000Z',
        },
        {
          conversationId: 'conv-2',
          title: 'Second',
          updatedAt: '2026-04-11T00:00:02.000Z',
        },
      ],
    });
    vi.mocked(transportClient.getUiMessages).mockImplementation(
      async (conversationId: string) => ({
        messages:
          conversationId === 'conv-2'
            ? [
                createUiMessage(
                  'u2',
                  'user',
                  'route-selected prompt',
                  '2026-04-11T00:00:03.000Z',
                ),
                createUiMessage(
                  'a2',
                  'assistant',
                  'route-selected answer',
                  '2026-04-11T00:00:04.000Z',
                ),
              ]
            : [
                createUiMessage(
                  'u1',
                  'user',
                  'default prompt',
                  '2026-04-11T00:00:00.000Z',
                ),
                createUiMessage(
                  'a1',
                  'assistant',
                  'default answer',
                  '2026-04-11T00:00:01.000Z',
                ),
              ],
      }),
    );

    render(
      <ChatWorkspace
        transportClient={transportClient}
        activeConversationId="conv-2"
        onActiveConversationIdChange={() => {}}
        onLogout={() => {}}
        onSessionExpired={() => {}}
      />,
    );

    await waitFor(() => {
      expect(screen.getByText('route-selected prompt')).toBeInTheDocument();
      expect(screen.getByText('route-selected answer')).toBeInTheDocument();
    });
    expect(transportClient.getUiMessages).toHaveBeenCalledWith('conv-2', 100);
  });

  it('keeps the newly created conversation visible when the host immediately controls the returned id', async () => {
    const transportClient = createTransportClient();

    function ControlledHarness() {
      const [activeConversationId, setActiveConversationId] = useState('');

      return (
        <ChatWorkspace
          transportClient={transportClient}
          activeConversationId={activeConversationId}
          onActiveConversationIdChange={setActiveConversationId}
          onLogout={() => {}}
          onSessionExpired={() => {}}
        />
      );
    }

    render(<ControlledHarness />);

    await screen.findByText('Starter Prompts');
    const textarea = await screen.findByPlaceholderText('Message the agent...');
    fireEvent.change(textarea, { target: { value: 'hello' } });
    fireEvent.click(screen.getByRole('button', { name: 'Send message' }));

    await waitFor(() => {
      expect(screen.getAllByText('hello').length).toBeGreaterThan(0);
      expect(screen.getByText('hello back')).toBeInTheDocument();
      expect(screen.queryByText('Starter Prompts')).not.toBeInTheDocument();
    });
  });
});
