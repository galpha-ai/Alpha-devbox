export interface VertexOpenAIMessage {
  role: 'system' | 'user' | 'assistant';
  content: string;
}

export interface VertexOpenAIConfig {
  projectId: string;
  location: string;
  model: string;
  endpoint: string;
  maxTokens: number;
  temperature: number;
}

interface VertexOpenAIChoice {
  message?: {
    content?: string | Array<{ text?: string }> | null;
    reasoning_content?: string | null;
  };
}

interface VertexOpenAIResponse {
  choices?: VertexOpenAIChoice[];
}

export const DEFAULT_VERTEX_OPENAI_MODEL = 'zai-org/glm-5-maas';

export function resolveAgentRuntime(env: NodeJS.ProcessEnv): string {
  return (env.DEVBOX_AGENT_RUNTIME || env.AGENT_RUNTIME || 'claude')
    .trim()
    .toLowerCase();
}

export function isVertexOpenAIRuntime(env: NodeJS.ProcessEnv): boolean {
  return new Set([
    'vertex-openai',
    'vertex_glm',
    'vertex-glm',
    'glm',
    'glm5',
    'glm-5',
    'openai-compatible',
  ]).has(resolveAgentRuntime(env));
}

export function resolveVertexOpenAIConfig(
  env: NodeJS.ProcessEnv,
): VertexOpenAIConfig {
  const projectId =
    env.VERTEX_OPENAI_PROJECT_ID ||
    env.GOOGLE_CLOUD_PROJECT ||
    env.GCLOUD_PROJECT ||
    env.ANTHROPIC_VERTEX_PROJECT_ID ||
    '';
  if (!projectId.trim()) {
    throw new Error(
      'Vertex OpenAI runtime requires VERTEX_OPENAI_PROJECT_ID or GOOGLE_CLOUD_PROJECT',
    );
  }

  const location =
    env.VERTEX_OPENAI_LOCATION || env.CLOUD_ML_REGION || 'global';
  const model = env.VERTEX_OPENAI_MODEL || DEFAULT_VERTEX_OPENAI_MODEL;
  const endpoint =
    env.VERTEX_OPENAI_BASE_URL ||
    buildVertexOpenAIEndpoint(projectId, location);
  const maxTokens = parsePositiveInteger(env.VERTEX_OPENAI_MAX_TOKENS, 4096);
  const temperature = parseFiniteNumber(env.VERTEX_OPENAI_TEMPERATURE, 0.2);

  return {
    projectId,
    location,
    model,
    endpoint,
    maxTokens,
    temperature,
  };
}

export function buildVertexOpenAIEndpoint(
  projectId: string,
  location: string,
): string {
  const host =
    location === 'global'
      ? 'https://aiplatform.googleapis.com'
      : `https://${location}-aiplatform.googleapis.com`;
  return `${host}/v1/projects/${projectId}/locations/${location}/endpoints/openapi/chat/completions`;
}

export function extractVertexOpenAIText(
  response: VertexOpenAIResponse,
): string {
  const message = response.choices?.[0]?.message;
  const content = message?.content;
  if (typeof content === 'string' && content.trim()) {
    return content;
  }
  if (Array.isArray(content)) {
    const text = content.map((part) => part.text || '').join('');
    if (text.trim()) return text;
  }
  if (typeof message?.reasoning_content === 'string') {
    return message.reasoning_content;
  }
  return '';
}

export async function callVertexOpenAIChat(
  messages: VertexOpenAIMessage[],
  env: NodeJS.ProcessEnv,
): Promise<string> {
  const config = resolveVertexOpenAIConfig(env);
  const accessToken = await resolveGoogleAccessToken(env);

  const response = await fetch(config.endpoint, {
    method: 'POST',
    headers: {
      Authorization: `Bearer ${accessToken}`,
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      model: config.model,
      messages,
      max_tokens: config.maxTokens,
      temperature: config.temperature,
    }),
  });

  const bodyText = await response.text();
  if (!response.ok) {
    throw new Error(
      `Vertex OpenAI request failed (${response.status}): ${bodyText.slice(0, 1000)}`,
    );
  }

  const body = JSON.parse(bodyText) as VertexOpenAIResponse;
  return extractVertexOpenAIText(body);
}

async function resolveGoogleAccessToken(
  env: NodeJS.ProcessEnv,
): Promise<string> {
  const explicitToken =
    env.GOOGLE_OAUTH_ACCESS_TOKEN || env.GOOGLE_ACCESS_TOKEN || '';
  if (explicitToken.trim()) return explicitToken.trim();

  const metadataHost = env.GCE_METADATA_HOST || 'metadata.google.internal';
  const metadataUrl = `http://${metadataHost}/computeMetadata/v1/instance/service-accounts/default/token`;

  try {
    const response = await fetch(metadataUrl, {
      headers: { 'Metadata-Flavor': 'Google' },
    });
    if (response.ok) {
      const body = (await response.json()) as { access_token?: string };
      if (body.access_token) return body.access_token;
    }
  } catch {
    /* local development commonly has no metadata server */
  }

  throw new Error(
    'Vertex OpenAI runtime requires GOOGLE_OAUTH_ACCESS_TOKEN locally or Google Cloud workload identity in deployment',
  );
}

function parsePositiveInteger(value: string | undefined, fallback: number) {
  if (!value) return fallback;
  const parsed = Number.parseInt(value, 10);
  return Number.isFinite(parsed) && parsed > 0 ? parsed : fallback;
}

function parseFiniteNumber(value: string | undefined, fallback: number) {
  if (!value) return fallback;
  const parsed = Number.parseFloat(value);
  return Number.isFinite(parsed) ? parsed : fallback;
}
