import { useCallback, useEffect, useMemo, useRef, useState } from 'react';
import { useChat } from '@ai-sdk/react';
import type { UIMessage } from 'ai';
import SpeechRecognition, {
  useSpeechRecognition,
} from 'react-speech-recognition';
import {
  Loader2,
  LogOut,
  Menu,
  Mic,
  MicOff,
  MessageSquare,
  Plus,
  Send,
  Sparkles,
  Trash2,
  X,
} from 'lucide-react';

import { StarterPromptGrid } from './StarterPromptGrid';
import { ChatTranscript } from './ChatTranscript';
import { getChatMessageText } from './chat-message';
import { ChatTransportError, type ChatTransportClient } from './transport';

const MOBILE_BREAKPOINT_PX = 1024;
const CHAT_UPDATE_THROTTLE_MS = 100;

type ChatPanelStatus = 'idle' | 'processing' | 'complete' | 'error';
type ChatMessageMetadata = {
  timestamp?: string;
  sender?: string;
  senderName?: string;
};
type ChatMessage = UIMessage<ChatMessageMetadata>;

interface ChatWorkspaceProps {
  transportClient: ChatTransportClient;
  activeConversationId?: string;
  onActiveConversationIdChange?: (conversationId: string) => void;
  onLogout: () => void | Promise<void>;
  onSessionExpired: () => void;
  sessionActionLabel?: string | null;
}

interface ConversationState {
  conversationId: string;
  title: string;
  messages: ChatMessage[];
  status: ChatPanelStatus;
  errorCode?: string | null;
  errorMessage?: string | null;
  hydrated: boolean;
}

export function ChatWorkspace({
  transportClient,
  activeConversationId: controlledActiveConversationId,
  onActiveConversationIdChange,
  onLogout,
  onSessionExpired,
  sessionActionLabel = null,
}: ChatWorkspaceProps) {
  const isControlledActiveConversation =
    controlledActiveConversationId !== undefined;
  const [isMobileViewport, setIsMobileViewport] = useState(() =>
    typeof window !== 'undefined'
      ? window.innerWidth < MOBILE_BREAKPOINT_PX
      : false,
  );
  const [conversations, setConversations] = useState<ConversationState[]>([]);
  const [internalActiveConversationId, setInternalActiveConversationId] =
    useState('');
  const [input, setInput] = useState('');
  const [sidebarOpen, setSidebarOpen] = useState(() =>
    typeof window !== 'undefined'
      ? window.innerWidth >= MOBILE_BREAKPOINT_PX
      : true,
  );
  const [isBootstrapping, setIsBootstrapping] = useState(true);
  const [shellError, setShellError] = useState<string | null>(null);
  const activeConversationId =
    controlledActiveConversationId ?? internalActiveConversationId;
  const activeConversationIdRef = useRef(activeConversationId);
  const pendingSubmitRef = useRef<{
    conversationId: string;
    prompt: string;
  } | null>(null);
  const hydrateRequestVersionRef = useRef(new Map<string, number>());
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const endRef = useRef<HTMLDivElement>(null);
  const pressToTalkActiveRef = useRef(false);
  const ignoreVoiceClickRef = useRef(false);
  const lastAppliedTranscriptRef = useRef('');
  const {
    transcript,
    listening: isListening,
    resetTranscript,
    browserSupportsSpeechRecognition,
    isMicrophoneAvailable,
  } = useSpeechRecognition();

  useEffect(() => {
    activeConversationIdRef.current = activeConversationId;
  }, [activeConversationId]);

  const setActiveConversationId = useCallback(
    (nextConversationId: string | ((current: string) => string)) => {
      const resolvedConversationId =
        typeof nextConversationId === 'function'
          ? nextConversationId(activeConversationIdRef.current)
          : nextConversationId;

      if (resolvedConversationId === activeConversationIdRef.current) {
        return;
      }

      if (!isControlledActiveConversation) {
        setInternalActiveConversationId(resolvedConversationId);
      }

      onActiveConversationIdChange?.(resolvedConversationId);
    },
    [isControlledActiveConversation, onActiveConversationIdChange],
  );

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

  const replaceConversationMessages = useCallback(
    (conversationId: string, nextMessages: ChatMessage[]) => {
      setConversations((currentConversations) =>
        currentConversations.map((conversation) => {
          if (conversation.conversationId !== conversationId) {
            return conversation;
          }

          const nextStatus = resolveHydratedChatStatus(nextMessages);

          return {
            ...conversation,
            title: deriveConversationTitle(
              trimTitle(conversation.title),
              toConversationTitleMessages(nextMessages),
              conversationId,
            ),
            messages: nextMessages,
            status: nextStatus,
            errorCode: null,
            errorMessage: null,
            hydrated: true,
          };
        }),
      );
    },
    [],
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

  const loadConversationMessages = useCallback(
    async (conversationId: string) => {
      const nextVersion =
        (hydrateRequestVersionRef.current.get(conversationId) ?? 0) + 1;
      hydrateRequestVersionRef.current.set(conversationId, nextVersion);

      try {
        const { messages } = await transportClient.getUiMessages<ChatMessage>(
          conversationId,
          100,
        );
        if (
          hydrateRequestVersionRef.current.get(conversationId) !== nextVersion
        ) {
          return;
        }
        replaceConversationMessages(
          conversationId,
          normalizeChatMessages(messages),
        );
      } catch (error) {
        if (
          hydrateRequestVersionRef.current.get(conversationId) !== nextVersion
        ) {
          return;
        }
        applyConversationError(conversationId, error);
      }
    },
    [applyConversationError, replaceConversationMessages, transportClient],
  );

  useEffect(() => {
    const textarea = textareaRef.current;
    if (!textarea) {
      return;
    }

    textarea.style.height = 'auto';
    textarea.style.height = `${Math.min(textarea.scrollHeight, 200)}px`;
  }, [input]);

  useEffect(() => {
    if (
      isListening ||
      !transcript.trim() ||
      transcript === lastAppliedTranscriptRef.current
    ) {
      return;
    }

    setInput((current) => appendSpeechTranscript(current, transcript.trim()));
    lastAppliedTranscriptRef.current = transcript;
    resetTranscript();
  }, [isListening, resetTranscript, transcript]);

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
      behavior: activeConversation?.status === 'processing' ? 'auto' : 'smooth',
    });
  }, [activeConversation?.messages, activeConversation?.status]);

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
        setConversations((current) =>
          mergeBootstrapConversations(current, nextConversations),
        );
        if (!isControlledActiveConversation) {
          setInternalActiveConversationId(
            (current) => current || nextConversations[0]?.conversationId || '',
          );
        }
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
  }, [isControlledActiveConversation, onSessionExpired, transportClient]);

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

    void loadConversationMessages(activeConversationId);
  }, [activeConversationId, conversations, loadConversationMessages]);

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
  }, [conversations, isMobileViewport, setActiveConversationId]);

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
    [onSessionExpired, setActiveConversationId, transportClient],
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

        updateConversation(conversationId, (current) => ({
          ...current,
          title: current.title !== 'New Chat' ? current.title : fallbackTitle,
          status: 'processing',
          hydrated: true,
          errorCode: null,
          errorMessage: null,
        }));
        pendingSubmitRef.current = { conversationId, prompt };
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
      onSessionExpired,
      setActiveConversationId,
      transportClient,
      updateConversation,
    ],
  );

  const handleSend = useCallback(() => {
    void handleSubmit(input);
  }, [handleSubmit, input]);

  const startVoiceInput = useCallback(() => {
    if (!browserSupportsSpeechRecognition || !isMicrophoneAvailable) {
      return;
    }

    lastAppliedTranscriptRef.current = '';
    resetTranscript();
    void SpeechRecognition.startListening({
      continuous: false,
      language:
        typeof navigator !== 'undefined' && navigator.language
          ? navigator.language
          : 'en-US',
    });
  }, [
    browserSupportsSpeechRecognition,
    isMicrophoneAvailable,
    resetTranscript,
  ]);

  const stopVoiceInput = useCallback(() => {
    void SpeechRecognition.stopListening();
  }, []);

  const handleVoiceInput = useCallback(() => {
    if (ignoreVoiceClickRef.current) {
      ignoreVoiceClickRef.current = false;
      return;
    }

    if (isListening) {
      stopVoiceInput();
      return;
    }

    startVoiceInput();
  }, [isListening, startVoiceInput, stopVoiceInput]);

  const handleVoicePointerDown = useCallback(() => {
    if (!browserSupportsSpeechRecognition || !isMicrophoneAvailable || isListening) {
      return;
    }

    pressToTalkActiveRef.current = true;
    ignoreVoiceClickRef.current = true;
    startVoiceInput();
  }, [
    browserSupportsSpeechRecognition,
    isListening,
    isMicrophoneAvailable,
    startVoiceInput,
  ]);

  const handleVoicePointerRelease = useCallback(() => {
    if (!pressToTalkActiveRef.current) {
      return;
    }

    pressToTalkActiveRef.current = false;
    stopVoiceInput();
  }, [stopVoiceInput]);

  const activeConversationView = useMemo(() => {
    if (!activeConversation) {
      return createDraftConversationState();
    }
    return activeConversation;
  }, [activeConversation]);

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

  const isRequestInFlight = conversations.some(
    (conversation) => conversation.status === 'processing',
  );
  const isHydratingConversation = Boolean(
    activeConversationId && activeConversation?.hydrated === false,
  );
  const canSend =
    input.trim().length > 0 &&
    !isRequestInFlight &&
    !isBootstrapping &&
    !isHydratingConversation;
  const isStarterState =
    activeConversationView.messages.length === 0 &&
    activeConversationView.status !== 'processing';
  const contentMaxWidthClass = isStarterState ? 'max-w-4xl' : 'max-w-[920px]';
  const speechSupported = browserSupportsSpeechRecognition;
  const composerHint = !speechSupported
    ? 'Voice input unavailable in this browser.'
    : !isMicrophoneAvailable
      ? 'Microphone permission was denied.'
    : isListening
      ? 'Listening… release the mic button to stop.'
      : 'Hold the mic button to talk. Enter to send. Shift+Enter for a new line.';

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
                  <ConversationSession
                    key={activeConversationView.conversationId || '__draft__'}
                    conversation={activeConversationView}
                    pendingPrompt={
                      pendingSubmitRef.current?.conversationId ===
                      activeConversationView.conversationId
                        ? pendingSubmitRef.current.prompt
                        : null
                    }
                    transportClient={transportClient}
                    onConversationUpdate={(updater) =>
                      updateConversation(
                        activeConversationView.conversationId,
                        updater,
                      )
                    }
                    onPromptHandled={() => {
                      const pending = pendingSubmitRef.current;
                      if (
                        pending?.conversationId ===
                        activeConversationView.conversationId
                      ) {
                        pendingSubmitRef.current = null;
                      }
                    }}
                    onRetry={handleRetry}
                    onError={applyConversationError}
                    onSessionExpired={onSessionExpired}
                    loadConversationMessages={loadConversationMessages}
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
                onClick={handleVoiceInput}
                onPointerDown={handleVoicePointerDown}
                onPointerUp={handleVoicePointerRelease}
                onPointerCancel={handleVoicePointerRelease}
                onPointerLeave={handleVoicePointerRelease}
                aria-label={isListening ? 'Stop voice input' : 'Start voice input'}
                disabled={!speechSupported}
                title={
                  speechSupported
                    ? isListening
                      ? 'Stop voice input'
                      : 'Hold to talk'
                    : 'Voice input unavailable in this browser'
                }
                className="m-1.5 rounded-xl border border-border/40 bg-background/50 p-2.5 text-muted-foreground transition-colors hover:bg-muted/60 hover:text-foreground disabled:cursor-not-allowed disabled:opacity-40"
              >
                {isListening ? (
                  <MicOff className="h-4 w-4" />
                ) : (
                  <Mic className="h-4 w-4" />
                )}
              </button>
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
              {composerHint}
            </p>
          </div>
        </div>
      </main>
    </div>
  );
}

function ConversationSession({
  conversation,
  pendingPrompt,
  transportClient,
  onConversationUpdate,
  onPromptHandled,
  onRetry,
  onError,
  onSessionExpired,
  loadConversationMessages,
}: {
  conversation: ConversationState;
  pendingPrompt: string | null;
  transportClient: ChatTransportClient;
  onConversationUpdate: (
    updater: (current: ConversationState) => ConversationState,
  ) => void;
  onPromptHandled: () => void;
  onRetry: () => void;
  onError: (conversationId: string, error: unknown) => void;
  onSessionExpired: () => void;
  loadConversationMessages: (conversationId: string) => Promise<void>;
}) {
  const lastSentPromptRef = useRef<string | null>(null);
  const {
    messages: liveMessages,
    sendMessage,
    status: chatStatus,
    clearError,
  } = useChat<ChatMessage>({
    id: conversation.conversationId || '__draft__',
    messages: conversation.messages,
    transport: transportClient.chatTransport,
    experimental_throttle: CHAT_UPDATE_THROTTLE_MS,
    onFinish: ({ messages, isAbort, isDisconnect, isError }) => {
      if (isAbort || isDisconnect || isError) {
        return;
      }

      const finishedMessages = Array.isArray(messages)
        ? normalizeChatMessages(messages as ChatMessage[])
        : [];

      onConversationUpdate((current) => {
        const nextMessages =
          finishedMessages.length > 0 ? finishedMessages : current.messages;

        return {
          ...current,
          title: deriveConversationTitle(
            trimTitle(current.title),
            toConversationTitleMessages(nextMessages),
            current.conversationId,
          ),
          messages: nextMessages,
          status: resolveHydratedChatStatus(nextMessages),
          errorCode: null,
          errorMessage: null,
          hydrated: true,
        };
      });

      if (!hasRenderableAssistantContent(finishedMessages)) {
        void loadConversationMessages(conversation.conversationId);
      }
    },
    onError: (error) => {
      onError(conversation.conversationId, error);
      const normalized = normalizeWorkspaceError(error);
      if (normalized.code === 'session_expired') {
        onSessionExpired();
      }
    },
  });

  useEffect(() => {
    if (!pendingPrompt) {
      lastSentPromptRef.current = null;
      return;
    }

    if (lastSentPromptRef.current === pendingPrompt) {
      return;
    }

    lastSentPromptRef.current = pendingPrompt;
    onPromptHandled();
    clearError();

    void sendMessage({ text: pendingPrompt }).catch((error) => {
      onError(conversation.conversationId, error);
    });
  }, [
    clearError,
    conversation.conversationId,
    onError,
    onPromptHandled,
    pendingPrompt,
    sendMessage,
  ]);

  const conversationView = useMemo(
    () => ({
      ...conversation,
      messages: mergeConversationMessages(
        conversation.messages,
        normalizeChatMessages(liveMessages),
      ),
      status:
        chatStatus === 'submitted' || chatStatus === 'streaming'
          ? 'processing'
          : chatStatus === 'error'
            ? 'error'
            : conversation.status,
    }),
    [chatStatus, conversation, liveMessages],
  );

  return (
    <ConversationThread conversation={conversationView} onRetry={onRetry} />
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
    return message.role === 'user' || content;
  });
  const hasLiveAssistantTurn = hasVisibleLatestAssistantTurn(
    conversation.messages,
  );

  return (
    <section className="space-y-4">
      <div className="space-y-4">
        <ChatTranscript messages={visibleMessages} />

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
          !hasRenderableAssistantContent(conversation.messages) && (
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

function createConversationState(
  conversationId: string,
  title = 'New Chat',
  messages: ChatMessage[] = [],
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

function mergeBootstrapConversations(
  currentConversations: ConversationState[],
  bootstrappedConversations: ConversationState[],
) {
  const bootstrappedById = new Map(
    bootstrappedConversations.map((conversation) => [
      conversation.conversationId,
      conversation,
    ]),
  );

  const mergedCurrent = currentConversations.map((conversation) => {
    const bootstrapped = bootstrappedById.get(conversation.conversationId);
    if (!bootstrapped) {
      return conversation;
    }

    bootstrappedById.delete(conversation.conversationId);

    if (
      conversation.messages.length > 0 ||
      conversation.status !== 'idle' ||
      conversation.hydrated
    ) {
      return {
        ...bootstrapped,
        ...conversation,
        title:
          conversation.title === 'New Chat'
            ? bootstrapped.title
            : conversation.title,
      };
    }

    return bootstrapped;
  });

  return [...mergedCurrent, ...bootstrappedById.values()];
}

function resolveHydratedChatStatus(messages: ChatMessage[]): ChatPanelStatus {
  if (hasRenderableAssistantContent(messages)) {
    return 'complete';
  }

  return messages.some((message) => message.role === 'user')
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

function hasRenderableAssistantContent(messages: ChatMessage[]) {
  return messages.some(
    (message) =>
      message.role === 'assistant' && getChatMessageText(message).trim(),
  );
}

function hasVisibleLatestAssistantTurn(messages: ChatMessage[]) {
  const latestMessage = [...messages]
    .reverse()
    .find((message) => message.role === 'assistant');
  if (!latestMessage) {
    return false;
  }

  return Boolean(getChatMessageText(latestMessage).trim());
}

function normalizeWorkspaceError(error: unknown) {
  if (error instanceof ChatTransportError) {
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

function appendSpeechTranscript(current: string, transcript: string) {
  if (!current.trim()) {
    return transcript;
  }

  return `${current.trimEnd()} ${transcript}`.trim();
}

function normalizeChatMessages(messages: ChatMessage[]) {
  return messages.map(normalizeChatMessage);
}

function mergeConversationMessages(
  canonicalMessages: ChatMessage[],
  liveMessages: ChatMessage[],
) {
  const merged = new Map<string, ChatMessage>();

  for (const message of normalizeChatMessages(canonicalMessages)) {
    merged.set(message.id, message);
  }

  for (const message of liveMessages) {
    merged.set(message.id, message);
  }

  return Array.from(merged.values());
}

function toConversationTitleMessages(messages: ChatMessage[]) {
  return messages.map((message) => ({
    role: message.role,
    content: getChatMessageText(message),
  }));
}

function normalizeChatMessage(message: ChatMessage): ChatMessage {
  if (message.role !== 'assistant') {
    return message;
  }

  return {
    ...message,
    role: 'assistant',
    metadata: {
      ...message.metadata,
      sender: message.metadata?.sender || 'Devbox',
      senderName: message.metadata?.senderName || 'Devbox',
      timestamp: message.metadata?.timestamp || new Date().toISOString(),
    },
    parts: Array.isArray(message.parts) ? message.parts : [],
  };
}
