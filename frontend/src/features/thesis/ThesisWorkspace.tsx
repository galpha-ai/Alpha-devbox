import { useCallback, useEffect, useMemo, useRef, useState } from 'react';
import { useChat } from '@ai-sdk/react';
import {
  Loader2,
  LogOut,
  Menu,
  MessageSquare,
  Plus,
  Send,
  Sparkles,
  Trash2,
  X,
} from 'lucide-react';

import { ArtifactRenderer } from './ArtifactRenderer';
import {
  buildConversationSnapshot,
  getChatMessageText,
  toThesisChatMessages,
  type ThesisArtifact,
  type ThesisChatMessage,
} from './devbox';
import {
  extractLatestSupportedArtifact,
  stripWrappedArtifactBlocks,
} from './protocol';
import { StarterPromptGrid } from './StarterPromptGrid';
import type { ThesisPanelStatus } from './ThesisResultPanel';
import { ThesisTransportError, type ThesisTransportClient } from './transport';
import { MarkdownChartRenderer } from './MarkdownChartRenderer';

const MOBILE_BREAKPOINT_PX = 1024;
const CHAT_UPDATE_THROTTLE_MS = 100;

const proseClasses = `prose prose-invert prose-sm max-w-none 
  prose-headings:text-foreground prose-headings:font-display
  prose-h2:text-lg prose-h3:text-base
  prose-p:text-muted-foreground prose-p:leading-relaxed
  prose-li:text-muted-foreground prose-li:leading-relaxed
  prose-strong:text-foreground prose-code:text-foreground`;

interface ThesisWorkspaceProps {
  transportClient: ThesisTransportClient;
  onLogout: () => void | Promise<void>;
  onSessionExpired: () => void;
  sessionActionLabel?: string | null;
}

interface ConversationState {
  conversationId: string;
  title: string;
  messages: ThesisChatMessage[];
  status: ThesisPanelStatus;
  errorCode?: string | null;
  errorMessage?: string | null;
  hydrated: boolean;
}

export function ThesisWorkspace({
  transportClient,
  onLogout,
  onSessionExpired,
  sessionActionLabel = null,
}: ThesisWorkspaceProps) {
  const [isMobileViewport, setIsMobileViewport] = useState(() =>
    typeof window !== 'undefined'
      ? window.innerWidth < MOBILE_BREAKPOINT_PX
      : false,
  );
  const [conversations, setConversations] = useState<ConversationState[]>([]);
  const [activeConversationId, setActiveConversationId] = useState('');
  const [input, setInput] = useState('');
  const [sidebarOpen, setSidebarOpen] = useState(() =>
    typeof window !== 'undefined'
      ? window.innerWidth >= MOBILE_BREAKPOINT_PX
      : true,
  );
  const [isBootstrapping, setIsBootstrapping] = useState(true);
  const [shellError, setShellError] = useState<string | null>(null);
  const activeConversationIdRef = useRef(activeConversationId);
  const pendingSubmitRef = useRef<{
    conversationId: string;
    prompt: string;
  } | null>(null);
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const endRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    activeConversationIdRef.current = activeConversationId;
  }, [activeConversationId]);

  const activeConversation = useMemo(
    () =>
      conversations.find(
        (conversation) => conversation.conversationId === activeConversationId,
      ) ?? null,
    [activeConversationId, conversations],
  );

  const updateConversation = useCallback(
    (
      conversationId: string,
      updater: (current: ConversationState) => ConversationState,
    ) => {
      setConversations((current) =>
        current.map((conversation) =>
          conversation.conversationId === conversationId
            ? updater(conversation)
            : conversation,
        ),
      );
    },
    [],
  );

  const replaceConversationFromSnapshot = useCallback(
    (
      conversationId: string,
      fallbackTitle: string,
      snapshot: ReturnType<typeof buildConversationSnapshot>,
    ) => {
      updateConversation(conversationId, (current) => {
        const nextMessages =
          snapshot.messages.length > 0
            ? toThesisChatMessages(snapshot.messages)
            : current.messages;
        const nextStatus =
          snapshot.messages.length > 0
            ? resolveHydratedStatus(snapshot)
            : current.status;
        const preserveError = nextStatus === 'processing';

        return {
          ...current,
          title: deriveConversationTitle(
            trimTitle(fallbackTitle || current.title),
            snapshot.messages,
            conversationId,
          ),
          messages: nextMessages,
          status: nextStatus,
          errorCode: preserveError ? (current.errorCode ?? null) : null,
          errorMessage: preserveError ? (current.errorMessage ?? null) : null,
          hydrated: true,
        };
      });
    },
    [updateConversation],
  );

  const applyConversationError = useCallback(
    (conversationId: string, error: unknown) => {
      const normalized = normalizeWorkspaceError(error);
      if (normalized.code === 'session_expired') {
        onSessionExpired();
      }

      updateConversation(conversationId, (current) => ({
        ...current,
        status: 'error',
        hydrated: true,
        errorCode: normalized.code,
        errorMessage: normalized.message,
      }));
    },
    [onSessionExpired, updateConversation],
  );

  const hydrateConversation = useCallback(
    async (conversationId: string) => {
      try {
        const { messages } = await transportClient.getMessages(
          conversationId,
          undefined,
          100,
        );
        const snapshot = buildConversationSnapshot(messages);
        const currentConversation = conversations.find(
          (conversation) => conversation.conversationId === conversationId,
        );

        replaceConversationFromSnapshot(
          conversationId,
          currentConversation?.title || `Chat ${conversationId.slice(0, 8)}`,
          snapshot,
        );
      } catch (error) {
        applyConversationError(conversationId, error);
      }
    },
    [
      applyConversationError,
      conversations,
      replaceConversationFromSnapshot,
      transportClient,
    ],
  );

  const {
    messages: liveMessages,
    setMessages: setLiveMessages,
    sendMessage,
    status: chatStatus,
    clearError,
  } = useChat<ThesisChatMessage>({
    id: activeConversationId || '__draft__',
    messages: activeConversation?.messages ?? [],
    transport: transportClient.chatTransport,
    experimental_throttle: CHAT_UPDATE_THROTTLE_MS,
    onFinish: ({ isAbort, isDisconnect, isError }) => {
      const conversationId = activeConversationIdRef.current;
      if (!conversationId || isAbort || isDisconnect || isError) {
        return;
      }

      void hydrateConversation(conversationId);
    },
    onError: (error) => {
      const conversationId = activeConversationIdRef.current;
      if (conversationId) {
        applyConversationError(conversationId, error);
        return;
      }

      handleShellError(error, onSessionExpired, setShellError);
    },
  });

  const activeLiveMessages = useMemo(
    () => normalizeChatMessages(liveMessages),
    [liveMessages],
  );

  useEffect(() => {
    if (!activeConversationId || !activeConversation?.hydrated) {
      return;
    }

    if (chatStatus === 'submitted' || chatStatus === 'streaming') {
      return;
    }

    const hydratedMessages = normalizeChatMessages(activeConversation.messages);
    if (
      getChatMessagesFingerprint(hydratedMessages) ===
      getChatMessagesFingerprint(activeLiveMessages)
    ) {
      return;
    }

    setLiveMessages(hydratedMessages);
  }, [
    activeConversation,
    activeConversationId,
    activeLiveMessages,
    chatStatus,
    setLiveMessages,
  ]);

  useEffect(() => {
    const pending = pendingSubmitRef.current;
    if (!pending || pending.conversationId !== activeConversationId) {
      return;
    }

    pendingSubmitRef.current = null;
    clearError();

    void sendMessage({ text: pending.prompt }).catch((error) => {
      applyConversationError(pending.conversationId, error);
    });
  }, [activeConversationId, applyConversationError, clearError, sendMessage]);

  useEffect(() => {
    const textarea = textareaRef.current;
    if (!textarea) {
      return;
    }

    textarea.style.height = 'auto';
    textarea.style.height = `${Math.min(textarea.scrollHeight, 200)}px`;
  }, [input]);

  useEffect(() => {
    if (typeof window === 'undefined') {
      return;
    }

    const syncViewportState = () => {
      const nextIsMobileViewport = window.innerWidth < MOBILE_BREAKPOINT_PX;
      setIsMobileViewport((current) => {
        if (current !== nextIsMobileViewport) {
          setSidebarOpen(!nextIsMobileViewport);
        }

        return nextIsMobileViewport;
      });
    };

    syncViewportState();
    window.addEventListener('resize', syncViewportState);

    return () => {
      window.removeEventListener('resize', syncViewportState);
    };
  }, []);

  useEffect(() => {
    endRef.current?.scrollIntoView({
      behavior:
        chatStatus === 'submitted' ||
        chatStatus === 'streaming' ||
        activeConversation?.status === 'processing'
          ? 'auto'
          : 'smooth',
    });
  }, [activeConversation?.status, activeLiveMessages, chatStatus]);

  useEffect(() => {
    let cancelled = false;

    async function bootstrap() {
      setIsBootstrapping(true);
      setShellError(null);

      try {
        const { conversations: listed } =
          await transportClient.listConversations();
        if (cancelled) {
          return;
        }

        const nextConversations = listed.map((conversation) =>
          createConversationState(
            conversation.conversationId,
            trimTitle(
              conversation.title ||
                `Chat ${conversation.conversationId.slice(0, 8)}`,
            ),
          ),
        );
        setConversations(nextConversations);
        setActiveConversationId(
          (current) => current || nextConversations[0]?.conversationId || '',
        );
      } catch (error) {
        if (!cancelled) {
          handleShellError(error, onSessionExpired, setShellError);
        }
      } finally {
        if (!cancelled) {
          setIsBootstrapping(false);
        }
      }
    }

    void bootstrap();

    return () => {
      cancelled = true;
    };
  }, [onSessionExpired, transportClient]);

  useEffect(() => {
    if (!activeConversationId) {
      return;
    }

    const conversation = conversations.find(
      (entry) => entry.conversationId === activeConversationId,
    );
    if (
      !conversation ||
      conversation.hydrated ||
      conversation.status === 'processing'
    ) {
      return;
    }

    void hydrateConversation(activeConversationId);
  }, [activeConversationId, conversations, hydrateConversation]);

  const handleCreateConversation = useCallback(() => {
    if (
      conversations.some((conversation) => conversation.status === 'processing')
    ) {
      return;
    }

    setActiveConversationId('');
    setInput('');
    setShellError(null);
    if (isMobileViewport) {
      setSidebarOpen(false);
    }
  }, [conversations, isMobileViewport]);

  const handleDeleteConversation = useCallback(
    async (conversationId: string) => {
      try {
        await transportClient.deleteConversation(conversationId);
        setConversations((current) => {
          const remaining = current.filter(
            (conversation) => conversation.conversationId !== conversationId,
          );
          setActiveConversationId((activeId) =>
            activeId === conversationId
              ? remaining[0]?.conversationId || ''
              : activeId,
          );
          return remaining;
        });

        if (activeConversationIdRef.current === conversationId) {
          setShellError(null);
        }
      } catch (error) {
        handleShellError(error, onSessionExpired, setShellError);
      }
    },
    [onSessionExpired, transportClient],
  );

  const handleSubmit = useCallback(
    async (rawPrompt: string, suggestedTitle?: string) => {
      const prompt = rawPrompt.trim();
      if (!prompt) {
        return;
      }

      setInput('');
      setShellError(null);

      const fallbackTitle = trimTitle(suggestedTitle || prompt);
      let conversationId = activeConversationIdRef.current;

      try {
        if (!conversationId) {
          const created = await transportClient.createConversation();
          conversationId = created.conversationId;
          pendingSubmitRef.current = { conversationId, prompt };
          const nextConversation = createConversationState(
            conversationId,
            fallbackTitle,
          );
          nextConversation.status = 'processing';
          nextConversation.hydrated = true;
          setConversations((current) => [nextConversation, ...current]);
          setActiveConversationId(conversationId);
          return;
        }

        clearError();
        updateConversation(conversationId, (current) => ({
          ...current,
          title: current.title !== 'New Chat' ? current.title : fallbackTitle,
          status: 'processing',
          hydrated: true,
          errorCode: null,
          errorMessage: null,
        }));

        await sendMessage({ text: prompt });
      } catch (error) {
        if (conversationId) {
          applyConversationError(conversationId, error);
        } else {
          handleShellError(error, onSessionExpired, setShellError);
        }
      }
    },
    [
      applyConversationError,
      clearError,
      onSessionExpired,
      sendMessage,
      transportClient,
      updateConversation,
    ],
  );

  const handleSend = useCallback(() => {
    void handleSubmit(input);
  }, [handleSubmit, input]);

  const activeConversationView = useMemo(() => {
    if (!activeConversation) {
      return createDraftConversationState();
    }

    return {
      ...activeConversation,
      messages: activeLiveMessages,
      status:
        chatStatus === 'submitted' || chatStatus === 'streaming'
          ? 'processing'
          : chatStatus === 'error'
            ? 'error'
            : activeConversation.status,
    };
  }, [activeConversation, activeLiveMessages, chatStatus]);

  const handleRetry = useCallback(() => {
    const lastUserMessage = [...activeConversationView.messages]
      .reverse()
      .find((message) => message.role === 'user');
    const prompt = lastUserMessage ? getChatMessageText(lastUserMessage) : '';
    if (!prompt) {
      return;
    }

    void handleSubmit(prompt, activeConversationView.title);
  }, [activeConversationView, handleSubmit]);

  const handleKeyDown = (event: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (event.key === 'Enter' && !event.shiftKey) {
      event.preventDefault();
      handleSend();
    }
  };

  const isRequestInFlight =
    chatStatus === 'submitted' ||
    chatStatus === 'streaming' ||
    conversations.some((conversation) => conversation.status === 'processing');
  const isHydratingConversation = Boolean(
    activeConversationId && activeConversation?.hydrated === false,
  );
  const canSend =
    input.trim().length > 0 &&
    !isRequestInFlight &&
    !isBootstrapping &&
    !isHydratingConversation;
  const isStarterState = activeConversationView.messages.length === 0;
  const contentMaxWidthClass = isStarterState ? 'max-w-4xl' : 'max-w-[920px]';

  return (
    <div className="relative flex h-screen overflow-hidden bg-background text-foreground">
      {isMobileViewport && sidebarOpen && (
        <button
          type="button"
          aria-label="Close conversation history"
          onClick={() => setSidebarOpen(false)}
          className="absolute inset-0 z-30 bg-black/50 lg:hidden"
        />
      )}

      <aside
        className={
          isMobileViewport
            ? `absolute inset-y-0 left-0 z-40 w-72 max-w-[85vw] overflow-hidden border-r border-border/50 bg-[hsl(0,0%,3%)] transition-transform duration-300 ${
                sidebarOpen ? 'translate-x-0' : '-translate-x-full'
              }`
            : `${sidebarOpen ? 'w-72' : 'w-0'} shrink-0 overflow-hidden border-r border-border/50 bg-[hsl(0,0%,3%)] transition-all duration-300`
        }
      >
        <div className="flex h-full flex-col">
          <div className="flex items-center justify-between border-b border-border/30 p-4">
            <div className="flex items-center gap-2">
              <Sparkles className="h-5 w-5 text-primary" />
              <span className="font-display text-lg font-semibold tracking-wide">
                Devbox
              </span>
            </div>
            <button
              type="button"
              aria-label="Close conversation history"
              onClick={() => setSidebarOpen(false)}
              className="rounded p-1 transition-colors hover:bg-muted"
            >
              <X className="h-4 w-4 text-muted-foreground" />
            </button>
          </div>

          <div className="p-3">
            <button
              type="button"
              onClick={() => void handleCreateConversation()}
              disabled={isRequestInFlight}
              className="flex w-full items-center gap-2 rounded-lg border border-border/60 px-4 py-2.5 text-sm text-muted-foreground transition-colors hover:bg-muted/40 hover:text-foreground disabled:cursor-not-allowed disabled:opacity-40"
            >
              <Plus className="h-4 w-4" />
              New Chat
            </button>
          </div>

          <div className="flex-1 overflow-y-auto px-2 pb-4">
            <div className="px-2 py-2 text-xs font-medium uppercase tracking-wider text-muted-foreground">
              Chats
            </div>
            {conversations.map((conversation) => {
              const isActive =
                activeConversationId === conversation.conversationId;

              return (
                <div
                  key={conversation.conversationId}
                  className={`group mb-0.5 flex items-center gap-1 rounded-lg pr-1 transition-all ${
                    isActive
                      ? 'bg-muted/80 text-foreground'
                      : 'text-muted-foreground hover:bg-muted/30 hover:text-foreground'
                  }`}
                >
                  <button
                    type="button"
                    disabled={isRequestInFlight}
                    onClick={() => {
                      setActiveConversationId(conversation.conversationId);
                      setShellError(null);
                      if (isMobileViewport) {
                        setSidebarOpen(false);
                      }
                    }}
                    className="flex min-w-0 flex-1 items-center gap-2 rounded-lg px-3 py-2.5 text-left text-sm disabled:cursor-not-allowed disabled:opacity-50"
                  >
                    <MessageSquare className="h-4 w-4 shrink-0 opacity-50" />
                    <span className="flex-1 truncate">
                      {conversation.title}
                    </span>
                  </button>
                  <button
                    type="button"
                    aria-label={`Delete ${conversation.title}`}
                    disabled={isRequestInFlight}
                    onClick={() => {
                      void handleDeleteConversation(
                        conversation.conversationId,
                      );
                    }}
                    className={`rounded-md p-1 text-muted-foreground transition hover:bg-muted/50 hover:text-foreground disabled:cursor-not-allowed disabled:opacity-40 ${
                      isActive
                        ? 'opacity-100'
                        : 'opacity-100 md:opacity-0 md:group-hover:opacity-100 md:group-focus-within:opacity-100'
                    }`}
                  >
                    <Trash2 className="h-3.5 w-3.5" />
                  </button>
                </div>
              );
            })}
          </div>

          {sessionActionLabel ? (
            <div className="space-y-3 border-t border-border/30 p-4">
              <button
                type="button"
                onClick={() => void onLogout()}
                className="flex w-full items-center gap-2 rounded-lg border border-border/40 px-3 py-2 text-sm text-muted-foreground transition-colors hover:bg-muted/30 hover:text-foreground"
              >
                <LogOut className="h-4 w-4" />
                {sessionActionLabel}
              </button>
            </div>
          ) : null}
        </div>
      </aside>

      <main className="flex min-w-0 flex-1 flex-col">
        <header className="flex h-14 items-center border-b border-border/30 bg-background/80 px-4 backdrop-blur-sm">
          {(isMobileViewport || !sidebarOpen) && (
            <button
              type="button"
              aria-label="Open conversation history"
              onClick={() => setSidebarOpen(true)}
              className="mr-3 rounded-lg p-2 transition-colors hover:bg-muted"
            >
              <Menu className="h-5 w-5 text-muted-foreground" />
            </button>
          )}
          <div className="flex min-w-0 flex-1 items-center gap-2">
            <MessageSquare className="h-4 w-4 shrink-0 text-primary" />
            <span className="truncate text-sm font-medium text-foreground">
              {activeConversationView.title || 'Devbox'}
            </span>
          </div>
          <div className="ml-2 flex items-center gap-1.5">
            <span className="h-1.5 w-1.5 rounded-full bg-muted-foreground/40" />
            <span className="text-[10px] text-muted-foreground/60">
              streaming
            </span>
          </div>
        </header>

        <div className="flex-1 overflow-y-auto">
          <div className={`mx-auto w-full ${contentMaxWidthClass} px-4 py-8`}>
            {shellError && (
              <div className="mb-6 rounded-xl border border-destructive/30 bg-destructive/10 px-4 py-3 text-sm text-destructive">
                {shellError}
              </div>
            )}

            {isBootstrapping || isHydratingConversation ? (
              <div className="rounded-2xl border border-border/40 bg-card/35 px-6 py-16 text-center text-sm text-muted-foreground">
                Restoring conversations...
              </div>
            ) : (
              <div className="space-y-5">
                {isStarterState ? (
                  <StarterPromptGrid
                    disabled={isRequestInFlight}
                    onSelectPrompt={(prompt, title) => {
                      if (isMobileViewport) {
                        setSidebarOpen(false);
                      }
                      void handleSubmit(prompt, title);
                    }}
                  />
                ) : (
                  <ConversationThread
                    conversation={activeConversationView}
                    onRetry={handleRetry}
                  />
                )}
                <div ref={endRef} />
              </div>
            )}
          </div>
        </div>

        <div className="shrink-0 border-t border-border/30 bg-background/70 backdrop-blur-sm">
          <div className={`mx-auto w-full ${contentMaxWidthClass} p-4`}>
            <div className="relative flex items-end rounded-2xl border border-border/60 bg-card/80 transition-colors focus-within:border-primary/40">
              <textarea
                ref={textareaRef}
                value={input}
                onChange={(event) => setInput(event.target.value)}
                onKeyDown={handleKeyDown}
                placeholder="Message the agent..."
                rows={1}
                className="max-h-[200px] flex-1 resize-none bg-transparent px-4 py-3.5 text-sm placeholder:text-muted-foreground/60 focus:outline-none"
              />
              <button
                type="button"
                onClick={handleSend}
                aria-label="Send message"
                disabled={!canSend}
                className="m-1.5 rounded-xl bg-primary p-2.5 text-primary-foreground transition-all hover:brightness-110 disabled:opacity-30 disabled:hover:brightness-100"
              >
                <Send className="h-4 w-4" />
              </button>
            </div>
            <p className="mt-2 text-center text-[10px] text-muted-foreground/50">
              Enter to send. Shift+Enter for a new line.
            </p>
          </div>
        </div>
      </main>
    </div>
  );
}

function ConversationThread({
  conversation,
  onRetry,
}: {
  conversation: ConversationState;
  onRetry: () => void;
}) {
  const visibleMessages = conversation.messages.filter((message) => {
    const content = getChatMessageText(message).trim();
    return (
      message.role === 'user' ||
      content ||
      message.metadata?.artifactOnly ||
      message.metadata?.artifact
    );
  });
  const hasLiveAssistantTurn = hasVisibleLatestAssistantTurn(
    conversation.messages,
  );

  return (
    <section className="space-y-4">
      <div className="space-y-4">
        {visibleMessages.map((message) => (
          <MessageBubble key={message.id} message={message} />
        ))}

        {conversation.status === 'processing' && !hasLiveAssistantTurn && (
          <div className="flex items-start gap-3">
            <div className="mt-1 flex h-8 w-8 items-center justify-center rounded-full border border-border/30 bg-card/70">
              <Loader2 className="h-4 w-4 animate-spin text-primary" />
            </div>
            <div className="max-w-[90%] rounded-2xl rounded-bl-md border border-border/30 bg-card/70 px-4 py-3 text-sm text-muted-foreground">
              {conversation.errorCode === 'concurrency_limit' &&
              conversation.errorMessage
                ? conversation.errorMessage
                : 'Assistant is working...'}
            </div>
          </div>
        )}

        {conversation.status === 'error' &&
          !hasAssistantText(conversation.messages) && (
            <div className="rounded-2xl border border-destructive/30 bg-destructive/10 px-4 py-4 text-sm text-destructive">
              <div className="font-medium">
                {mapConversationErrorTitle(conversation.errorCode)}
              </div>
              <p className="mt-2 leading-relaxed">
                {mapConversationErrorBody(
                  conversation.errorCode,
                  conversation.errorMessage,
                )}
              </p>
              <button
                type="button"
                onClick={onRetry}
                className="mt-4 rounded-xl border border-destructive/30 bg-background/70 px-4 py-2 text-sm font-medium text-foreground transition-colors hover:bg-background"
              >
                Retry request
              </button>
            </div>
          )}
      </div>
    </section>
  );
}

function MessageBubble({ message }: { message: ThesisChatMessage }) {
  const content = getChatMessageText(message).trim();
  const artifact = message.metadata?.artifact ?? null;

  if (message.role === 'user') {
    return (
      <div className="flex justify-end">
        <div className="min-w-0 max-w-[85%] whitespace-pre-wrap break-words rounded-2xl rounded-br-md bg-muted/60 px-4 py-3 text-sm leading-relaxed text-foreground [overflow-wrap:anywhere]">
          {content}
        </div>
      </div>
    );
  }

  return (
    <div className="flex items-start gap-3">
      <div className="mt-1 flex h-8 w-8 items-center justify-center rounded-full border border-border/30 bg-card/70">
        <Sparkles className="h-4 w-4 text-primary" />
      </div>
      <div className="min-w-0 max-w-[85%] space-y-3">
        {content ? (
          <div className="min-w-0 overflow-hidden rounded-2xl rounded-bl-md border border-border/30 bg-card/70 px-4 py-3">
            <MarkdownChartRenderer
              markdown={content}
              proseClassName={proseClasses}
            />
          </div>
        ) : null}
        {artifact ? <InlineArtifactCard artifact={artifact} /> : null}
        {!content && !artifact && message.metadata?.artifactOnly ? (
          <div className="rounded-2xl rounded-bl-md border border-border/30 bg-card/70 px-4 py-3 text-sm text-foreground">
            Generated a structured artifact.
          </div>
        ) : null}
      </div>
    </div>
  );
}

function InlineArtifactCard({ artifact }: { artifact: ThesisArtifact }) {
  const [collapsed, setCollapsed] = useState(true);
  const title = artifact.data.title;
  const summary = summarizeArtifact(artifact);
  const badge = artifact.type === 'chart_v1' ? 'Chart' : 'Report';

  return (
    <div className="min-w-0 overflow-hidden rounded-2xl border border-border/30 bg-card/70 px-4 py-3">
      <div className="flex flex-wrap items-center gap-2">
        <span className="rounded-full border border-primary/20 bg-primary/10 px-2 py-0.5 text-[10px] font-medium uppercase tracking-[0.18em] text-primary">
          {badge}
        </span>
        <div className="min-w-0 flex-1 text-sm font-medium text-foreground">
          {title}
        </div>
        <button
          type="button"
          onClick={() => setCollapsed((current) => !current)}
          className="rounded-lg border border-border/40 px-3 py-1 text-xs text-muted-foreground transition-colors hover:bg-muted hover:text-foreground"
        >
          {collapsed ? 'Expand' : 'Collapse'}
        </button>
      </div>

      {collapsed ? (
        <p className="mt-3 text-sm leading-relaxed text-muted-foreground">
          {summary}
        </p>
      ) : (
        <div className="mt-4">
          <ArtifactRenderer artifact={artifact} />
        </div>
      )}
    </div>
  );
}

function summarizeArtifact(artifact: ThesisArtifact) {
  const normalized = artifact.data.summary_markdown
    .replace(/[`*_>#-]/g, ' ')
    .replace(/\[(.*?)\]\((.*?)\)/g, '$1')
    .replace(/\s+/g, ' ')
    .trim();

  if (!normalized) {
    return 'No summary provided.';
  }

  return normalized.length > 140
    ? `${normalized.slice(0, 140)}...`
    : normalized;
}

function createConversationState(
  conversationId: string,
  title = 'New Chat',
  messages: ThesisChatMessage[] = [],
): ConversationState {
  return {
    conversationId,
    title,
    messages,
    status: messages.length > 0 ? 'complete' : 'idle',
    hydrated: messages.length > 0,
    errorCode: null,
    errorMessage: null,
  };
}

function createDraftConversationState(): ConversationState {
  return {
    ...createConversationState('', 'Devbox', []),
    status: 'idle',
    hydrated: true,
  };
}

function resolveHydratedStatus(
  snapshot: ReturnType<typeof buildConversationSnapshot>,
): ThesisPanelStatus {
  if (snapshot.latestArtifact) {
    return 'complete';
  }

  const hasAssistantReply = snapshot.messages.some(
    (message) => message.role === 'assistant',
  );
  if (hasAssistantReply) {
    return 'complete';
  }

  return snapshot.messages.some((message) => message.role === 'user')
    ? 'processing'
    : 'idle';
}

function deriveConversationTitle(
  currentTitle: string,
  messages: Array<{ role: 'user' | 'assistant'; content: string }>,
  conversationId: string,
) {
  if (
    currentTitle &&
    currentTitle !== 'New Chat' &&
    currentTitle !== 'Devbox'
  ) {
    return currentTitle;
  }

  const firstUserMessage = messages.find((message) => message.role === 'user');
  return trimTitle(
    firstUserMessage?.content || `Chat ${conversationId.slice(0, 8)}`,
  );
}

function trimTitle(value: string) {
  return value.length > 48 ? `${value.slice(0, 48)}...` : value;
}

function hasAssistantText(messages: ThesisChatMessage[]) {
  return messages.some(
    (message) =>
      message.role === 'assistant' && getChatMessageText(message).trim(),
  );
}

function hasVisibleLatestAssistantTurn(messages: ThesisChatMessage[]) {
  const latestMessage = [...messages]
    .reverse()
    .find((message) => message.role === 'assistant');
  if (!latestMessage) {
    return false;
  }

  return Boolean(
    getChatMessageText(latestMessage).trim() ||
    latestMessage.metadata?.artifactOnly,
  );
}

function normalizeWorkspaceError(error: unknown) {
  if (error instanceof ThesisTransportError) {
    return {
      code:
        error.status === 401
          ? 'session_expired'
          : error.code || 'transport_error',
      message: error.message,
    };
  }

  if (error instanceof Error && error.message === 'Authentication expired') {
    return {
      code: 'session_expired',
      message: 'Your session expired. Sign in again and retry.',
    };
  }

  return {
    code: 'transport_error',
    message:
      error instanceof Error ? error.message : 'Unexpected assistant error',
  };
}

function handleShellError(
  error: unknown,
  onSessionExpired: () => void,
  setShellError: (message: string | null) => void,
) {
  const normalized = normalizeWorkspaceError(error);
  if (normalized.code === 'session_expired') {
    onSessionExpired();
  }

  setShellError(normalized.message);
}

function mapConversationErrorTitle(errorCode?: string | null) {
  if (errorCode === 'session_expired') {
    return 'Session expired';
  }

  if (errorCode === 'concurrency_limit') {
    return 'System busy';
  }

  if (errorCode === 'timeout') {
    return 'No assistant reply';
  }

  return 'Request failed';
}

function mapConversationErrorBody(
  errorCode?: string | null,
  errorMessage?: string | null,
) {
  if (errorCode === 'session_expired') {
    return 'Your login session expired before the assistant replied. Sign in again and retry the request.';
  }

  if (errorCode === 'concurrency_limit') {
    return (
      errorMessage ||
      'The devbox queue is saturated right now. Wait a moment and retry.'
    );
  }

  if (errorCode === 'timeout') {
    return (
      errorMessage ||
      'The assistant did not write back a reply before the timeout window elapsed.'
    );
  }

  return (
    errorMessage ||
    'No stable assistant reply was returned. Retry the request or simplify the prompt.'
  );
}

function normalizeChatMessages(messages: ThesisChatMessage[]) {
  const deduped: ThesisChatMessage[] = [];

  for (const message of messages) {
    const nextMessage = normalizeChatMessage(message);
    const previousMessage = deduped[deduped.length - 1];

    if (isDuplicateAssistantChatMessage(previousMessage, nextMessage)) {
      continue;
    }

    deduped.push(nextMessage);
  }

  return deduped;
}

function normalizeChatMessage(message: ThesisChatMessage): ThesisChatMessage {
  if (message.role !== 'assistant') {
    return message;
  }

  const content = getChatMessageText(message);
  const artifact = extractLatestSupportedArtifact(content);
  const strippedContent = stripWrappedArtifactBlocks(content);

  return {
    ...message,
    role: 'assistant',
    metadata: {
      ...message.metadata,
      sender: message.metadata?.sender || 'Devbox',
      senderName: message.metadata?.senderName || 'Devbox',
      timestamp: message.metadata?.timestamp || new Date().toISOString(),
      artifact,
      artifactOnly: Boolean(artifact) && !strippedContent.trim(),
    },
    parts: strippedContent
      ? [
          {
            type: 'text',
            text: strippedContent,
            state: 'done',
          },
        ]
      : [],
  };
}

function isDuplicateAssistantChatMessage(
  previousMessage: ThesisChatMessage | undefined,
  currentMessage: ThesisChatMessage,
) {
  if (!previousMessage) {
    return false;
  }

  if (
    previousMessage.role !== 'assistant' ||
    currentMessage.role !== 'assistant'
  ) {
    return false;
  }

  return (
    getChatMessageText(previousMessage).trim() ===
      getChatMessageText(currentMessage).trim() &&
    Boolean(previousMessage.metadata?.artifactOnly) ===
      Boolean(currentMessage.metadata?.artifactOnly) &&
    getArtifactFingerprint(previousMessage.metadata?.artifact ?? null) ===
      getArtifactFingerprint(currentMessage.metadata?.artifact ?? null)
  );
}

function getChatMessagesFingerprint(messages: ThesisChatMessage[]) {
  return messages
    .map((message) => {
      const artifact = message.metadata?.artifact;

      return [
        message.role,
        message.id,
        getChatMessageText(message).trim(),
        message.metadata?.artifactOnly ? 'artifact-only' : 'content',
        artifact ? `${artifact.type}:${artifact.data.title}` : '',
      ].join(':');
    })
    .join('|');
}

function getArtifactFingerprint(artifact: ThesisArtifact | null) {
  if (!artifact) {
    return '';
  }

  return `${artifact.type}:${artifact.data.title}`;
}
