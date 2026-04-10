import type { ChatTransport, UIMessageChunk } from "ai";

import {
  buildConversationSnapshot,
  buildLatestAssistantTurn,
  getChatMessageText,
  getLatestUserChatMessage,
  toThesisChatMessages,
  type ThesisChatMessage,
  type ThesisConversationSnapshot,
} from "./devbox";
import {
  type ThesisQueuedResponse,
  type ThesisTransportClient,
  ThesisTransportError,
} from "./transport";
import type { DevboxWsClient, DevboxWsMessage } from "./wsTransport";

const INITIAL_POLL_INTERVAL_MS = import.meta.env.MODE === "test" ? 10 : 1500;
const ACTIVE_POLL_INTERVAL_MS = import.meta.env.MODE === "test" ? 10 : 1000;
const POLL_TIMEOUT_MS = import.meta.env.MODE === "test" ? 500 : 600_000;
const REQUIRED_STABLE_POLLS = 2;
const ARTIFACT_ONLY_REPLY = "Generated a structured artifact.";

export interface ThesisChatPollConfig {
  initialPollIntervalMs?: number;
  activePollIntervalMs?: number;
  timeoutMs?: number;
  requiredStablePolls?: number;
  timeoutMessage?: string;
}

export interface ThesisChatTransportOptions {
  transportClient: ThesisTransportClient;
  getConversationId: () => string;
  wsClient?: DevboxWsClient;
  onConversationCreated?: (event: {
    conversationId: string;
    title: string;
    messages: ThesisChatMessage[];
  }) => void;
  onConversationQueued?: (event: {
    conversationId: string;
    queuedResponse: ThesisQueuedResponse;
  }) => void;
  onConversationSettled?: (event: {
    conversationId: string;
    title: string;
    snapshot: ThesisConversationSnapshot;
    queuedResponse: ThesisQueuedResponse;
  }) => void;
  pollConfig?: ThesisChatPollConfig;
}

export function createThesisChatTransport(
  options: ThesisChatTransportOptions,
): ChatTransport<ThesisChatMessage> {
  const { transportClient } = options;

  return {
    async sendMessages({ messages, abortSignal, body }) {
      const latestUserMessage = getLatestUserChatMessage(messages);
      const prompt = latestUserMessage ? getChatMessageText(latestUserMessage).trim() : "";
      if (!prompt) {
        throw new Error("Message content is required");
      }

      const suggestedTitle = resolveSuggestedTitle(body) ?? prompt;

      let conversationId = options.getConversationId();
      if (!conversationId) {
        const created = await transportClient.createConversation();
        conversationId = created.conversationId;
        options.onConversationCreated?.({
          conversationId,
          title: suggestedTitle,
          messages,
        });
      }

      const queuedResponse = await transportClient.sendMessage(
        conversationId,
        prompt,
      );
      options.onConversationQueued?.({
        conversationId,
        queuedResponse,
      });

      const useWebSocket = options.wsClient?.isConnected() ?? false;

      if (useWebSocket) {
        return createWsAssistantReplyStream({
          abortSignal,
          conversationId,
          title: suggestedTitle,
          wsClient: options.wsClient!,
          transportClient,
          onConversationSettled: (settled) => {
            options.onConversationSettled?.({
              conversationId,
              title: settled.title,
              snapshot: settled.snapshot,
              queuedResponse,
            });
          },
        });
      }

      return createAssistantReplyStream({
        abortSignal,
        conversationId,
        title: suggestedTitle,
        transportClient,
        queuedResponse,
        pollConfig: options.pollConfig,
        onConversationSettled: (settled) => {
          options.onConversationSettled?.({
            conversationId,
            title: settled.title,
            snapshot: settled.snapshot,
            queuedResponse,
          });
        },
      });
    },

    async reconnectToStream() {
      return null;
    },
  };
}

function createAssistantReplyStream({
  abortSignal,
  conversationId,
  title,
  transportClient,
  queuedResponse,
  pollConfig,
  onConversationSettled,
}: {
  abortSignal?: AbortSignal;
  conversationId: string;
  title: string;
  transportClient: ThesisTransportClient;
  queuedResponse: ThesisQueuedResponse;
  pollConfig?: ThesisChatPollConfig;
  onConversationSettled: (settled: SettledConversationTurn) => void;
}) {
  const messageId = `assistant-${Date.now()}`;

  return new ReadableStream<UIMessageChunk>({
    async start(controller) {
      controller.enqueue({
        type: "start",
        messageMetadata: {
          artifactOnly: false,
          sender: "assistant",
          senderName: "Assistant",
        },
      });
      controller.enqueue({ type: "text-start", id: messageId });

      try {
        const settled = await streamConversationTurn({
          abortSignal,
          conversationId,
          controller,
          messageId,
          title,
          transportClient,
          pollConfig,
        });

        onConversationSettled(settled);
        controller.enqueue({ type: "text-end", id: messageId });
        controller.enqueue({
          type: "finish",
          messageMetadata: {
            artifactOnly: settled.artifactOnly,
            timestamp: settled.timestamp,
            sender: "assistant",
            senderName: "Assistant",
          },
        });
        controller.close();
      } catch (error) {
        const errorMessage = error instanceof Error ? error.message : "Unexpected assistant error";

        if (
          queuedResponse.code === "concurrency_limit"
          && errorMessage.includes("timed out before any stable reply")
        ) {
          controller.enqueue({
            type: "text-delta",
            id: messageId,
            delta: queuedResponse.message || "System busy, your request is queued.",
          });
          controller.enqueue({ type: "text-end", id: messageId });
          controller.enqueue({
            type: "finish",
            messageMetadata: {
              artifactOnly: false,
              sender: "assistant",
              senderName: "Assistant",
            },
          });
          controller.close();
          return;
        }

        controller.error(error);
      }
    },
  });
}

async function streamConversationTurn({
  abortSignal,
  conversationId,
  controller,
  messageId,
  title,
  transportClient,
  pollConfig,
}: {
  abortSignal?: AbortSignal;
  conversationId: string;
  controller: ReadableStreamDefaultController<UIMessageChunk>;
  messageId: string;
  title: string;
  transportClient: ThesisTransportClient;
  pollConfig?: ThesisChatPollConfig;
}) {
  const config = resolvePollConfig(pollConfig);
  let unchangedPolls = 0;
  let previousFingerprint = "";
  const startedAt = Date.now();

  while (Date.now() - startedAt < config.timeoutMs) {
    throwIfAborted(abortSignal);

    const response = await transportClient.getMessages(conversationId, undefined, 100);
    const messages = response?.messages ?? [];
    const snapshot = buildConversationSnapshot(messages);
    const latestTurn = buildLatestAssistantTurn(snapshot.messages);

    if (latestTurn.messages.length === 0) {
      await sleep(config.initialPollIntervalMs, abortSignal);
      continue;
    }

    if (latestTurn.fingerprint === previousFingerprint) {
      unchangedPolls += 1;
    } else {
      unchangedPolls = 1;
      previousFingerprint = latestTurn.fingerprint;
    }

    const hasArtifact = hasLatestArtifact(snapshot, latestTurn);

    if (hasArtifact || (latestTurn.transcript && unchangedPolls >= config.requiredStablePolls)) {
      return finalizeConversationTurn({
        title,
        snapshot,
        latestTurn,
        controller,
        messageId,
      });
    }

    await sleep(config.activePollIntervalMs, abortSignal);
  }

  const response = await transportClient.getMessages(conversationId, undefined, 100);
  const messages = response?.messages ?? [];
  const snapshot = buildConversationSnapshot(messages);
  const latestTurn = buildLatestAssistantTurn(snapshot.messages);
  const hasArtifact = hasLatestArtifact(snapshot, latestTurn);

  if (latestTurn.transcript || hasArtifact) {
    return finalizeConversationTurn({
      title,
      snapshot,
      latestTurn,
      controller,
      messageId,
    });
  }

  throw new ThesisTransportError(
    config.timeoutMessage,
    504,
    "timeout",
  );
}

function resolvePollConfig(override?: ThesisChatPollConfig): Required<ThesisChatPollConfig> {
  return {
    initialPollIntervalMs: override?.initialPollIntervalMs ?? INITIAL_POLL_INTERVAL_MS,
    activePollIntervalMs: override?.activePollIntervalMs ?? ACTIVE_POLL_INTERVAL_MS,
    timeoutMs: override?.timeoutMs ?? POLL_TIMEOUT_MS,
    requiredStablePolls: override?.requiredStablePolls ?? REQUIRED_STABLE_POLLS,
    timeoutMessage:
      override?.timeoutMessage ?? "The assistant request timed out before any stable reply was returned.",
  };
}

function finalizeConversationTurn({
  title,
  snapshot,
  latestTurn,
  controller,
  messageId,
}: {
  title: string;
  snapshot: ThesisConversationSnapshot;
  latestTurn: ReturnType<typeof buildLatestAssistantTurn>;
  controller: ReadableStreamDefaultController<UIMessageChunk>;
  messageId: string;
}): SettledConversationTurn {
  const finalContent = resolveStreamContent(snapshot, latestTurn);
  if (finalContent) {
    controller.enqueue({ type: "text-delta", id: messageId, delta: finalContent });
  }

  return {
    title,
    snapshot,
    content: finalContent,
    artifactOnly: !latestTurn.transcript && Boolean(hasLatestArtifact(snapshot, latestTurn) || latestTurn.artifactOnly),
    timestamp: latestTurn.messages.at(-1)?.timestamp,
  };
}

function resolveStreamContent(
  snapshot: ThesisConversationSnapshot,
  latestTurn: ReturnType<typeof buildLatestAssistantTurn>,
) {
  return latestTurn.transcript || (hasLatestArtifact(snapshot, latestTurn) ? ARTIFACT_ONLY_REPLY : "");
}

function hasLatestArtifact(
  snapshot: ThesisConversationSnapshot,
  latestTurn: ReturnType<typeof buildLatestAssistantTurn>,
) {
  return Boolean(
    snapshot.latestArtifact
    && latestTurn.messages.some((message) => message.id === snapshot.latestArtifactMessageId),
  );
}

interface SettledConversationTurn {
  title: string;
  snapshot: ThesisConversationSnapshot;
  content: string;
  artifactOnly: boolean;
  timestamp?: string;
}

function resolveSuggestedTitle(body: unknown) {
  if (body && typeof body === "object" && "suggestedTitle" in body && typeof body.suggestedTitle === "string") {
    return body.suggestedTitle.trim() || null;
  }

  return null;
}

async function sleep(ms: number, abortSignal?: AbortSignal) {
  if (!abortSignal) {
    await new Promise((resolve) => globalThis.setTimeout(resolve, ms));
    return;
  }

  await new Promise<void>((resolve, reject) => {
    const timeoutId = globalThis.setTimeout(() => {
      abortSignal.removeEventListener("abort", onAbort);
      resolve();
    }, ms);

    const onAbort = () => {
      globalThis.clearTimeout(timeoutId);
      abortSignal.removeEventListener("abort", onAbort);
      reject(new DOMException("Aborted", "AbortError"));
    };

    abortSignal.addEventListener("abort", onAbort, { once: true });
  });
}

function throwIfAborted(abortSignal?: AbortSignal) {
  if (abortSignal?.aborted) {
    throw new DOMException("Aborted", "AbortError");
  }
}

function createWsAssistantReplyStream({
  abortSignal,
  conversationId,
  title,
  wsClient,
  transportClient,
  onConversationSettled,
}: {
  abortSignal?: AbortSignal;
  conversationId: string;
  title: string;
  wsClient: DevboxWsClient;
  transportClient: ThesisTransportClient;
  onConversationSettled: (settled: SettledConversationTurn) => void;
}) {
  const messageId = `assistant-${Date.now()}`;

  return new ReadableStream<UIMessageChunk>({
    start(controller) {
      controller.enqueue({
        type: "start",
        messageMetadata: {
          artifactOnly: false,
          sender: "assistant",
          senderName: "Assistant",
        },
      });
      controller.enqueue({ type: "text-start", id: messageId });

      let outputBuffer = "";
      let settled = false;

      const unsubscribe = wsClient.subscribe((message: DevboxWsMessage) => {
        if (settled) return;
        if (message.type === "pong") return;
        if ("conversationId" in message && message.conversationId !== conversationId) return;

        if (message.type === "output") {
          outputBuffer += message.content;
          controller.enqueue({
            type: "text-delta",
            id: messageId,
            delta: message.content,
          });
        }

        if (message.type === "status" && (message.status === "success" || message.status === "error" || message.status === "idle")) {
          settled = true;
          unsubscribe();
          void finalizeWsStream({
            conversationId,
            title,
            transportClient,
            controller,
            messageId,
            outputBuffer,
            onConversationSettled,
          });
        }

        if (message.type === "error") {
          settled = true;
          unsubscribe();
          controller.enqueue({
            type: "text-delta",
            id: messageId,
            delta: message.message || "An error occurred.",
          });
          controller.enqueue({ type: "text-end", id: messageId });
          controller.enqueue({
            type: "finish",
            messageMetadata: {
              artifactOnly: false,
              sender: "assistant",
              senderName: "Assistant",
            },
          });
          controller.close();
        }
      });

      if (abortSignal) {
        abortSignal.addEventListener("abort", () => {
          if (!settled) {
            settled = true;
            unsubscribe();
            controller.error(new DOMException("Aborted", "AbortError"));
          }
        }, { once: true });
      }
    },
  });
}

async function finalizeWsStream({
  conversationId,
  title,
  transportClient,
  controller,
  messageId,
  outputBuffer,
  onConversationSettled,
}: {
  conversationId: string;
  title: string;
  transportClient: ThesisTransportClient;
  controller: ReadableStreamDefaultController<UIMessageChunk>;
  messageId: string;
  outputBuffer: string;
  onConversationSettled: (settled: SettledConversationTurn) => void;
}) {
  try {
    const response = await transportClient.getMessages(conversationId, undefined, 100);
    const messages = response?.messages ?? [];
    const snapshot = buildConversationSnapshot(messages);

    onConversationSettled({
      title,
      snapshot,
      content: outputBuffer,
      artifactOnly: !outputBuffer.trim() && Boolean(snapshot.latestArtifact),
      timestamp: snapshot.messages.at(-1)?.timestamp,
    });
  } catch {
    // Best-effort finalization
  }

  controller.enqueue({ type: "text-end", id: messageId });
  controller.enqueue({
    type: "finish",
    messageMetadata: {
      artifactOnly: false,
      sender: "assistant",
      senderName: "Assistant",
    },
  });
  controller.close();
}
