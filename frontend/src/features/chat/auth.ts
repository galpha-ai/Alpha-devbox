export const AUTH_STORAGE_KEYS = {
  accessToken: "access_token",
  refreshToken: "refresh_token",
  user: "user",
} as const;

const SEEDED_SESSION_BLOCK_KEY = "thesis_seeded_session_blocked_seed";
const LOCAL_DEV_USER_ID_STORAGE_KEY = "thesis_local_dev_user_id";

export interface AuthUser {
  id: string;
  address: string;
  email: string | null;
  username: string | null;
  display_name: string | null;
  avatar_url: string | null;
  created_at: string;
  last_login_at: string;
  chain_id: string;
}

export interface AuthSession {
  accessToken: string | null;
  refreshToken: string | null;
  user: AuthUser | null;
}

export interface AuthEnvSeed {
  accessToken?: string;
  refreshToken?: string;
  user?: string;
  localUserId?: string;
}

export interface AuthChallengeRequest {
  domain: string;
  chain_id: string;
  address: string;
}

export interface AuthChallengeResponse {
  challenge_id: string;
  message: string;
  expires_at: string;
}

export interface AuthVerifyRequest {
  challenge_id: string;
  signature: string;
}

export interface AuthVerifyResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
  expires_in: number;
  user: AuthUser;
}

export interface AuthRefreshResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
  expires_in: number;
}

interface ApiEnvelope<T> {
  data: T;
}

interface AuthClientOptions {
  baseUrl: string;
  fetch?: typeof fetch;
  storage?: Storage;
}

const LOCAL_DEV_ACCESS_TOKEN = "local-dev-access-token";

export function resolveLocalDevUserId(
  storage: Storage,
  configuredLocalUserId?: string,
  createId: () => string = () => globalThis.crypto.randomUUID(),
) {
  const explicitUserId = configuredLocalUserId?.trim();
  if (explicitUserId) {
    storage.setItem(LOCAL_DEV_USER_ID_STORAGE_KEY, explicitUserId);
    return explicitUserId;
  }

  const persistedUserId = storage
    .getItem(LOCAL_DEV_USER_ID_STORAGE_KEY)
    ?.trim();
  if (persistedUserId) {
    return persistedUserId;
  }

  const currentSession = readAuthSession(storage);
  const migratedUserId =
    isLocalDevAccessToken(currentSession.accessToken) &&
    currentSession.user?.id?.trim()
      ? currentSession.user.id.trim()
      : null;
  if (migratedUserId) {
    storage.setItem(LOCAL_DEV_USER_ID_STORAGE_KEY, migratedUserId);
    return migratedUserId;
  }

  const nextUserId = createId();
  storage.setItem(LOCAL_DEV_USER_ID_STORAGE_KEY, nextUserId);
  return nextUserId;
}

export function ensureMockAuthSession(storage: Storage, localUserId: string): AuthSession {
  writeAuthSession(storage, {
    accessToken: LOCAL_DEV_ACCESS_TOKEN,
    refreshToken: null,
    user: createLocalDevUser(localUserId),
  });

  return readAuthSession(storage);
}

export function resolveApiBaseUrl(
  isDev: boolean,
  configuredBaseUrl: string | undefined,
  fallbackBaseUrl: string,
) {
  return normalizeBaseUrl(configuredBaseUrl || fallbackBaseUrl);
}

export function readAuthSession(storage: Storage): AuthSession {
  const accessToken = storage.getItem(AUTH_STORAGE_KEYS.accessToken);
  const refreshToken = storage.getItem(AUTH_STORAGE_KEYS.refreshToken);
  const user = parseStoredUser(storage.getItem(AUTH_STORAGE_KEYS.user));

  return {
    accessToken,
    refreshToken,
    user,
  };
}

export function getAccessToken(storage: Storage = window.localStorage): string | null {
  return storage.getItem(AUTH_STORAGE_KEYS.accessToken);
}

export function seedAuthSessionFromEnv(
  storage: Storage,
  isDev: boolean,
  seed: AuthEnvSeed,
): AuthSession {
  const current = readAuthSession(storage);
  if (!isDev || current.accessToken) {
    return current;
  }

  const blockedSeedFingerprint = storage.getItem(SEEDED_SESSION_BLOCK_KEY);
  const currentSeedFingerprint = getSeededSessionFingerprint(seed);
  if (blockedSeedFingerprint && currentSeedFingerprint === blockedSeedFingerprint) {
    return current;
  }

  if (seed.accessToken?.trim()) {
    writeAuthSession(storage, {
      accessToken: seed.accessToken.trim(),
      refreshToken: seed.refreshToken?.trim() || null,
      user: parseStoredUser(seed.user ?? null),
    });

    return readAuthSession(storage);
  }

  if (seed.localUserId?.trim()) {
    writeAuthSession(storage, {
      accessToken: LOCAL_DEV_ACCESS_TOKEN,
      refreshToken: null,
      user: createLocalDevUser(seed.localUserId.trim()),
    });

    return readAuthSession(storage);
  }

  return current;
}

export function writeAuthSession(storage: Storage, session: AuthSession) {
  writeStorageValue(storage, AUTH_STORAGE_KEYS.accessToken, session.accessToken);
  writeStorageValue(storage, AUTH_STORAGE_KEYS.refreshToken, session.refreshToken);

  if (session.user) {
    storage.setItem(AUTH_STORAGE_KEYS.user, JSON.stringify(session.user));
  } else {
    storage.removeItem(AUTH_STORAGE_KEYS.user);
  }
}

export function clearAuthSession(storage: Storage) {
  writeAuthSession(storage, {
    accessToken: null,
    refreshToken: null,
    user: null,
  });
}

export function blockSeededAuthSession(storage: Storage, seed: AuthEnvSeed) {
  const fingerprint = getSeededSessionFingerprint(seed);
  if (!fingerprint) {
    storage.removeItem(SEEDED_SESSION_BLOCK_KEY);
    return;
  }

  storage.setItem(SEEDED_SESSION_BLOCK_KEY, fingerprint);
}

export function clearSeededAuthSessionBlock(storage: Storage) {
  storage.removeItem(SEEDED_SESSION_BLOCK_KEY);
}

export function encodeEthereumSignatureToBase64(signature: string) {
  const hex = signature.startsWith("0x") ? signature.slice(2) : signature;
  if (!hex || hex.length % 2 !== 0 || /[^0-9a-f]/i.test(hex)) {
    throw new Error("Invalid Ethereum signature");
  }

  const bytes = new Uint8Array(hex.length / 2);
  for (let index = 0; index < hex.length; index += 2) {
    bytes[index / 2] = Number.parseInt(hex.slice(index, index + 2), 16);
  }

  return encodeBase64(bytes);
}

export function isLocalDevAccessToken(token: string | null | undefined) {
  return token === LOCAL_DEV_ACCESS_TOKEN;
}

export function createAuthClient(options: AuthClientOptions) {
  const fetchImpl = options.fetch ?? globalThis.fetch.bind(globalThis);
  const storage = options.storage ?? window.localStorage;
  const baseUrl = normalizeBaseUrl(options.baseUrl);

  async function challenge(request: AuthChallengeRequest): Promise<AuthChallengeResponse> {
    return requestJson<AuthChallengeResponse>(`${baseUrl}/api/user-service/v1/auth/challenge`, {
      method: "POST",
      body: JSON.stringify(request),
    });
  }

  async function verify(request: AuthVerifyRequest): Promise<AuthVerifyResponse> {
    const response = await requestJson<AuthVerifyResponse>(`${baseUrl}/api/user-service/v1/auth/verify`, {
      method: "POST",
      body: JSON.stringify(request),
    });

    writeAuthSession(storage, {
      accessToken: response.access_token,
      refreshToken: response.refresh_token,
      user: response.user,
    });

    return response;
  }

  async function refresh(): Promise<AuthRefreshResponse> {
    const session = readAuthSession(storage);
    if (!session.refreshToken) {
      clearAuthSession(storage);
      throw new Error("Authentication expired");
    }

    try {
      const response = await requestJson<AuthRefreshResponse>(`${baseUrl}/api/user-service/v1/auth/refresh`, {
        method: "POST",
        body: JSON.stringify({
          refresh_token: session.refreshToken,
        }),
      });

      writeAuthSession(storage, {
        accessToken: response.access_token,
        refreshToken: response.refresh_token,
        user: session.user,
      });

      return response;
    } catch {
      clearAuthSession(storage);
      throw new Error("Authentication expired");
    }
  }

  async function logout() {
    const session = readAuthSession(storage);

    if (session.refreshToken) {
      try {
        await requestJson(`${baseUrl}/api/user-service/v1/auth/logout`, {
          method: "POST",
          body: JSON.stringify({
            refresh_token: session.refreshToken,
          }),
        });
      } catch {
        // Ignore logout API errors and clear local auth state anyway.
      }
    }

    clearAuthSession(storage);
  }

  async function authFetch(input: string, init?: RequestInit, allowRetry = true): Promise<Response> {
    const session = readAuthSession(storage);
    if (!session.accessToken) {
      throw new Error("Authentication required");
    }

    const headers = buildHeaders(init, session.accessToken);
    if (isLocalDevAccessToken(session.accessToken) && session.user?.id && !headers["X-User-Id"] && !headers["x-user-id"]) {
      headers["X-User-Id"] = session.user.id;
    }

    const response = await fetchImpl(resolveUrl(baseUrl, input), {
      ...init,
      headers,
    });

    if (response.status !== 401 || !allowRetry || isLocalDevAccessToken(session.accessToken)) {
      return response;
    }

    await refresh();
    return authFetch(input, init, false);
  }

  function getSession() {
    return readAuthSession(storage);
  }

async function requestJson<T = unknown>(input: string, init: RequestInit): Promise<T> {
    const response = await fetchImpl(input, {
      ...init,
      headers: buildHeaders(init),
    });
    const payload = await parseJson<{ data?: T; error?: string }>(response);

    if (!response.ok) {
      throw new Error(payload?.error || `Request failed (${response.status})`);
    }

    if (payload && typeof payload === "object" && "data" in payload && payload.data !== undefined) {
      return payload.data;
    }

    return payload as T;
  }

  return {
    authFetch,
    challenge,
    getSession,
    logout,
    refresh,
    verify,
  };
}

function createLocalDevUser(localUserId: string): AuthUser {
  const now = new Date().toISOString();

  return {
    id: localUserId,
    address: `local:${localUserId}`,
    email: null,
    username: localUserId,
    display_name: "Local Demo",
    avatar_url: null,
    created_at: now,
    last_login_at: now,
    chain_id: "local:web",
  };
}

function getSeededSessionFingerprint(seed: AuthEnvSeed) {
  if (seed.accessToken?.trim()) {
    return `access:${seed.accessToken.trim()}`;
  }

  if (seed.localUserId?.trim()) {
    return `local:${seed.localUserId.trim()}`;
  }

  return null;
}

function buildHeaders(init?: RequestInit, accessToken?: string) {
  const headers = normalizeHeaders(init?.headers);
  if (!headers["Content-Type"] && !headers["content-type"] && init?.body && !(init.body instanceof FormData)) {
    headers["Content-Type"] = "application/json";
  }
  if (accessToken) {
    headers.Authorization = `Bearer ${accessToken}`;
  }
  return headers;
}

function normalizeHeaders(headers?: HeadersInit) {
  if (!headers) {
    return {} as Record<string, string>;
  }

  if (headers instanceof Headers) {
    return Object.fromEntries(headers.entries());
  }

  if (Array.isArray(headers)) {
    return Object.fromEntries(headers);
  }

  return { ...headers };
}

function encodeBase64(bytes: Uint8Array) {
  let binary = "";
  for (const value of bytes) {
    binary += String.fromCharCode(value);
  }

  return globalThis.btoa(binary);
}

function parseStoredUser(value: string | null): AuthUser | null {
  if (!value) {
    return null;
  }

  try {
    return JSON.parse(value) as AuthUser;
  } catch {
    return null;
  }
}

async function parseJson<T>(response: Response): Promise<T | null> {
  try {
    return await response.json();
  } catch {
    return null;
  }
}

function resolveUrl(baseUrl: string, path: string) {
  if (/^https?:\/\//.test(path)) {
    return path;
  }

  return `${baseUrl}${path}`;
}

function normalizeBaseUrl(value: string) {
  return value.replace(/\/+$/, "");
}

function writeStorageValue(storage: Storage, key: string, value: string | null) {
  if (value) {
    storage.setItem(key, value);
  } else {
    storage.removeItem(key);
  }
}
