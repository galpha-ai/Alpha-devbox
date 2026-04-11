import type { UIMessage } from "ai";

import {
  extractLatestSupportedArtifact,
  stripWrappedArtifactBlocks,
  type ChartArtifactV1,
  type ThesisReportV1,
} from "./protocol";
import type { ThesisPromptMode } from "./transport";

export interface DevboxApiMessage {
  id: string;
  chat_jid: string;
  thread_id: string;
  sender: string;
  sender_name: string;
  content: string;
  timestamp: string;
  is_bot_message: number | boolean;
}

export interface ThesisConversationMessage {
  id: string;
  role: "user" | "assistant";
  content: string;
  timestamp: string;
  sender: string;
  senderName: string;
  artifact?: ThesisArtifact | null;
  artifactOnly?: boolean;
  requestMode?: ThesisPromptMode;
}

export interface ThesisChatMessageMetadata {
  timestamp?: string;
  sender?: string;
  senderName?: string;
  artifact?: ThesisArtifact | null;
  artifactOnly?: boolean;
  requestMode?: ThesisPromptMode;
}

export type ThesisChatMessage = UIMessage<ThesisChatMessageMetadata>;

export interface ThesisConversationSnapshot {
  messages: ThesisConversationMessage[];
  assistantTranscript: string;
  latestArtifact: ThesisArtifact | null;
  latestArtifactMessageId: string | null;
  latestArtifactTimestamp: string | null;
  latestUserPromptMode: ThesisPromptMode | null;
}

export type ThesisArtifact =
  | {
      type: "chart_v1";
      data: ChartArtifactV1;
    }
  | {
      type: "thesis_report_v1";
      data: ThesisReportV1;
    };

export function buildConversationSnapshot(
  apiMessages: DevboxApiMessage[],
): ThesisConversationSnapshot {
  const orderedMessages = [...apiMessages].sort(compareMessagesAscending);
  const latestUserMessage = [...orderedMessages]
    .reverse()
    .find((message) => !isAssistantMessage(message));

  const messages = collapseAdjacentDuplicateAssistantMessages(
    orderedMessages.map<ThesisConversationMessage>((message) => {
      const role = isAssistantMessage(message) ? "assistant" : "user";
      const artifact = role === "assistant" ? extractLatestSupportedArtifact(message.content) : null;
      const strippedContent = role === "user"
        ? stripThesisPromptPreamble(message.content)
        : stripWrappedArtifactBlocks(message.content);
      const artifactOnly = role === "assistant"
        && Boolean(artifact)
        && !strippedContent.trim();

      return {
        id: message.id,
        role,
        content: strippedContent,
        timestamp: message.timestamp,
        sender: message.sender,
        senderName: message.sender_name,
        artifact,
        artifactOnly,
        requestMode: role === "user" ? detectPromptMode(message.content) : undefined,
      };
    }),
  );
  const latestArtifactMessage = [...messages]
    .reverse()
    .find((message) => message.role === "assistant" && message.artifact);
  const latestArtifactEntry = latestArtifactMessage
    ? orderedMessages.find((message) => message.id === latestArtifactMessage.id)
    : null;
  const latestResolvedArtifact = latestArtifactMessage?.artifact ?? null;

  const assistantTranscript = messages
    .filter((message) => message.role === "assistant")
    .map((message) => message.content.trim())
    .filter(Boolean)
    .join("\n\n");

  return {
    messages,
    assistantTranscript,
    latestArtifact: latestResolvedArtifact,
    latestArtifactMessageId: latestArtifactMessage?.id ?? null,
    latestArtifactTimestamp: latestArtifactEntry?.timestamp ?? latestArtifactMessage?.timestamp ?? null,
    latestUserPromptMode: latestUserMessage ? detectPromptMode(latestUserMessage.content) : null,
  };
}

function compareMessagesAscending(left: DevboxApiMessage, right: DevboxApiMessage) {
  const timestampDelta = Date.parse(left.timestamp) - Date.parse(right.timestamp);
  if (timestampDelta !== 0) {
    return timestampDelta;
  }

  return left.id.localeCompare(right.id);
}

function collapseAdjacentDuplicateAssistantMessages(
  messages: ThesisConversationMessage[],
) {
  const deduped: ThesisConversationMessage[] = [];

  for (const message of messages) {
    const previous = deduped[deduped.length - 1];
    if (isDuplicateAssistantMessage(previous, message)) {
      continue;
    }
    deduped.push(message);
  }

  return deduped;
}

function isDuplicateAssistantMessage(
  previous: ThesisConversationMessage | undefined,
  current: ThesisConversationMessage,
) {
  if (!previous) return false;
  if (previous.role !== "assistant" || current.role !== "assistant") return false;

  return (
    normalizeAssistantContent(previous.content) === normalizeAssistantContent(current.content)
    && getConversationArtifactFingerprint(previous.artifact ?? null) === getConversationArtifactFingerprint(current.artifact ?? null)
    && Boolean(previous.artifactOnly) === Boolean(current.artifactOnly)
  );
}

function normalizeAssistantContent(content: string) {
  return content.trim();
}

function isAssistantMessage(message: DevboxApiMessage) {
  return message.is_bot_message === 1 || message.is_bot_message === true;
}

function stripThesisPromptPreamble(content: string) {
  const marker = "\n\nUser request:\n";
  const index = content.indexOf(marker);
  if (index === -1) {
    return content;
  }

  return content.slice(index + marker.length).trim() || content;
}

function detectPromptMode(content: string): ThesisPromptMode {
  return content.includes("CHART_V1") || content.includes("THESIS_REPORT_V1") ? "artifact" : "chat";
}

export function toThesisChatMessages(
  messages: ThesisConversationMessage[],
): ThesisChatMessage[] {
  return messages.map((message) => ({
    id: message.id,
    role: message.role,
    metadata: {
      timestamp: message.timestamp,
      sender: message.sender,
      senderName: message.senderName,
      artifact: message.artifact ?? null,
      artifactOnly: message.artifactOnly,
      requestMode: message.requestMode,
    },
    parts: message.content
      ? [{
          type: "text",
          text: message.content,
          state: "done",
        }]
      : [],
  }));
}

export function toConversationMessages(
  messages: ThesisChatMessage[],
): ThesisConversationMessage[] {
  return messages.map((message) => ({
    id: message.id,
    role: message.role === "assistant" ? "assistant" : "user",
    content: getChatMessageText(message),
    timestamp: message.metadata?.timestamp ?? "",
    sender: message.metadata?.sender ?? (message.role === "assistant" ? "assistant" : "user"),
    senderName: message.metadata?.senderName ?? (message.role === "assistant" ? "Assistant" : "You"),
    artifact: message.metadata?.artifact ?? null,
    artifactOnly: Boolean(message.metadata?.artifactOnly),
    requestMode: message.metadata?.requestMode,
  }));
}

export function collapseAdjacentDuplicateChatMessages(
  messages: ThesisChatMessage[],
): ThesisChatMessage[] {
  const deduped: ThesisChatMessage[] = [];

  for (const message of messages) {
    const previous = deduped[deduped.length - 1];
    if (isDuplicateAssistantChatMessage(previous, message)) {
      continue;
    }
    deduped.push(message);
  }

  return deduped;
}

export function getChatMessageText(message: ThesisChatMessage) {
  return message.parts
    .filter((part): part is Extract<typeof part, { type: "text" }> => part.type === "text")
    .map((part) => part.text)
    .join("");
}

export function buildChatMessageFingerprint(messages: ThesisChatMessage[]) {
  return messages
    .map((message) => [
      message.id,
      message.role,
      getChatMessageText(message),
      message.metadata?.timestamp ?? "",
      getArtifactFingerprint(message.metadata?.artifact ?? null),
      message.metadata?.artifactOnly ? "artifact" : "text",
    ].join(":"))
    .join("|");
}

export function getLatestUserChatMessage(messages: ThesisChatMessage[]) {
  return [...messages].reverse().find((message) => message.role === "user");
}

export function getLatestUserChatMessageMode(messages: ThesisChatMessage[]) {
  return getLatestUserChatMessage(messages)?.metadata?.requestMode ?? null;
}

export function buildLatestAssistantTurn(messages: ThesisConversationMessage[]) {
  const latestUserIndex = [...messages]
    .map((message, index) => ({ message, index }))
    .reverse()
    .find(({ message }) => message.role === "user")?.index;

  if (latestUserIndex === undefined) {
    return {
      messages: [] as ThesisConversationMessage[],
      transcript: "",
      fingerprint: "",
      artifactOnly: false,
    };
  }

  const assistantMessages = messages
    .slice(latestUserIndex + 1)
    .filter((message) => message.role === "assistant");

  return {
    messages: assistantMessages,
    transcript: assistantMessages
      .map((message) => message.content.trim())
      .filter(Boolean)
      .join("\n\n"),
    fingerprint: assistantMessages
      .map((message) => [
        message.id,
        message.timestamp,
        message.content,
        getConversationArtifactFingerprint(message.artifact ?? null),
      ].join(":"))
      .join("|"),
    artifactOnly: assistantMessages.some((message) => message.artifactOnly) && assistantMessages.every((message) => !message.content.trim()),
  };
}

function getArtifactFingerprint(artifact: ThesisArtifact | null) {
  if (!artifact) {
    return "";
  }

  return `${artifact.type}:${artifact.data.title}`;
}

function isDuplicateAssistantChatMessage(
  previous: ThesisChatMessage | undefined,
  current: ThesisChatMessage,
) {
  if (!previous) return false;
  if (previous.role !== "assistant" || current.role !== "assistant") return false;

  return (
    getChatMessageText(previous).trim() === getChatMessageText(current).trim()
    && getArtifactFingerprint(previous.metadata?.artifact ?? null)
      === getArtifactFingerprint(current.metadata?.artifact ?? null)
    && Boolean(previous.metadata?.artifactOnly) === Boolean(current.metadata?.artifactOnly)
  );
}

function getConversationArtifactFingerprint(artifact: ThesisConversationMessage["artifact"]) {
  return getArtifactFingerprint(artifact ?? null);
}
