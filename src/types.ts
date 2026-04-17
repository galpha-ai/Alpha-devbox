export interface ContainerConfig {
  timeout?: number;
}

export interface RegisteredAgent {
  name: string;
  agentName: string;
  trigger: string;
  added_at: string;
  containerConfig?: ContainerConfig;
  requiresTrigger?: boolean; // Default: true for channels, false for DMs
}

/** @deprecated use RegisteredAgent */
export type RegisteredGroup = RegisteredAgent;

export interface NewMessage {
  id: string;
  chat_jid: string;
  thread_id?: string | null;
  sender: string;
  sender_name: string;
  content: string;
  timestamp: string;
  is_from_me?: boolean;
  is_bot_message?: boolean;
  ui_message_json?: string | null;
}

export interface SendMessageOptions {
  threadId?: string | null;
}

export interface StatusIndicatorOptions {
  messageId?: string;
  threadId?: string | null;
}

export interface ScheduledTask {
  id: string;
  agentName: string;
  chat_jid: string;
  prompt: string;
  schedule_type: 'cron' | 'interval' | 'once';
  schedule_value: string;
  context_mode: 'group' | 'isolated';
  next_run: string | null;
  last_run: string | null;
  last_result: string | null;
  status: 'active' | 'paused' | 'completed';
  created_at: string;
}

export interface TaskRunLog {
  task_id: string;
  run_at: string;
  duration_ms: number;
  status: 'success' | 'error';
  result: string | null;
  error: string | null;
}

// --- Channel abstraction ---

export interface Channel {
  name: string;
  connect(): Promise<void>;
  sendMessage(
    jid: string,
    text: string,
    options?: SendMessageOptions,
  ): Promise<void>;
  isConnected(): boolean;
  ownsJid(jid: string): boolean;
  disconnect(): Promise<void>;
  // Optional: typing indicator. Channels that support it implement it.
  // Status can be: 'processing' (agent working), 'success' (completed successfully),
  // 'error' (failed), or 'idle' (no active work)
  setTyping?(
    jid: string,
    status: 'processing' | 'success' | 'error' | 'idle',
    options?: StatusIndicatorOptions,
  ): Promise<void>;
}

// Callback type that channels use to deliver inbound messages
export type OnInboundMessage = (chatJid: string, message: NewMessage) => void;

// Callback for chat metadata discovery.
// name is optional — channels that deliver names inline (Telegram) pass it here;
// channels that sync names separately (WhatsApp syncGroupMetadata) omit it.
export type OnChatMetadata = (
  chatJid: string,
  timestamp: string,
  name?: string,
  channel?: string,
  isGroup?: boolean,
) => void;
