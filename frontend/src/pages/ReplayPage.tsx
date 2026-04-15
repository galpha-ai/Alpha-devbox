import { useEffect, useMemo, useRef, useState } from "react";
import { useParams, useSearchParams } from "react-router-dom";
import { MessageSquare } from "lucide-react";

import {
  ChatTranscript,
  type ChatTranscriptMessage,
} from "@/features/chat/ChatTranscript";
import {
  ChatTransportError,
  createReplayTransportClient,
} from "@/features/chat/transport";

export default function ReplayPage() {
  const { replayId = "" } = useParams();
  const [searchParams] = useSearchParams();
  const replyId = searchParams.get("reply");
  const [messages, setMessages] = useState<ChatTranscriptMessage[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const messageRefs = useRef<Record<string, HTMLElement | null>>({});
  const replayClient = useMemo(() => createReplayTransportClient(), []);

  useEffect(() => {
    let cancelled = false;

    async function loadReplay() {
      setLoading(true);
      setError(null);
      try {
        const response =
          await replayClient.getReplayUiMessages<ChatTranscriptMessage>(
          replayId,
        );
        if (!cancelled) {
          setMessages(response.messages ?? []);
        }
      } catch (err) {
        if (!cancelled) {
          setError(normalizeReplayError(err));
        }
      } finally {
        if (!cancelled) {
          setLoading(false);
        }
      }
    }

    if (!replayId) {
      setError("Replay unavailable");
      setLoading(false);
      return;
    }

    void loadReplay();
    return () => {
      cancelled = true;
    };
  }, [replayClient, replayId]);

  useEffect(() => {
    if (!replyId) return;
    const target = messageRefs.current[replyId];
    if (!target) return;
    target.scrollIntoView({ block: "center", behavior: "smooth" });
    target.focus();
  }, [messages, replyId]);

  const title = useMemo(() => {
    const firstUserMessage = messages.find((message) => message.role === "user");
    const firstText = firstUserMessage
      ? firstUserMessage.parts
          .filter(
            (part): part is Extract<typeof part, { type: "text" }> =>
              part.type === "text",
          )
          .map((part) => part.text)
          .join("")
          .trim()
      : "";

    if (!firstText) {
      return `Chat ${replayId.slice(0, 8)}`;
    }

    return firstText.length > 48 ? `${firstText.slice(0, 48)}...` : firstText;
  }, [messages, replayId]);

  return (
    <div className="relative flex h-screen overflow-hidden bg-background text-foreground">
      <main className="flex min-w-0 flex-1 flex-col">
        <header className="flex h-14 items-center border-b border-border/30 bg-background/80 px-4 backdrop-blur-sm">
          <div className="flex min-w-0 flex-1 items-center gap-2">
            <MessageSquare className="h-4 w-4 shrink-0 text-primary" />
            <span className="truncate text-sm font-medium text-foreground">
              {title}
            </span>
          </div>
          <div className="ml-2 flex items-center gap-1.5">
            <span className="h-1.5 w-1.5 rounded-full bg-muted-foreground/40" />
            <span className="text-[10px] text-muted-foreground/60">
              replay
            </span>
          </div>
        </header>

        <div className="flex-1 overflow-y-auto">
          <div className="mx-auto w-full max-w-[920px] px-4 py-8">
            {loading ? (
              <div className="rounded-2xl border border-border/40 bg-card/35 px-6 py-16 text-center text-sm text-muted-foreground">
                Loading replay...
              </div>
            ) : null}

            {!loading && error ? (
              <div className="rounded-2xl border border-destructive/30 bg-destructive/10 px-4 py-4 text-sm text-destructive">
                <div className="font-medium">Replay unavailable</div>
                <p className="mt-2 leading-relaxed">{error}</p>
              </div>
            ) : null}

            {!loading && !error ? (
              <div className="space-y-5">
                <ChatTranscript
                  messages={messages}
                  highlightedMessageId={replyId}
                  messageRefMap={messageRefs}
                />
              </div>
            ) : null}
          </div>
        </div>
      </main>
    </div>
  );
}

function normalizeReplayError(error: unknown) {
  if (error instanceof ChatTransportError) {
    return error.message;
  }
  if (error instanceof Error) {
    return error.message;
  }
  return "Failed to load replay.";
}
