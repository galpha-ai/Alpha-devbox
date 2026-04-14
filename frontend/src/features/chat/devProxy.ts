import type { IncomingMessage } from "node:http";

import type { ProxyOptions } from "vite";

export const DEFAULT_LOCAL_DEVBOX_PROXY_TARGET = "http://127.0.0.1:18092";
export const DEFAULT_CHAT_DEV_PROXY_TARGET = DEFAULT_LOCAL_DEVBOX_PROXY_TARGET;

export interface ChatDevProxyTargets {
  devbox: string;
  userService: string;
  localUserId?: string;
}

export function resolveChatDevProxyTarget(configuredBaseUrl?: string) {
  return resolveChatDevProxyTargets({ apiBaseUrl: configuredBaseUrl }).devbox;
}

export function resolveChatDevProxyTargets({
  apiBaseUrl,
  devboxBaseUrl,
  userServiceBaseUrl,
  localUserId,
}: {
  apiBaseUrl?: string;
  devboxBaseUrl?: string;
  userServiceBaseUrl?: string;
  localUserId?: string;
}): ChatDevProxyTargets {
  const defaultTarget = normalizeBaseUrl(apiBaseUrl || DEFAULT_CHAT_DEV_PROXY_TARGET);
  const normalizedLocalUserId = localUserId?.trim() || undefined;
  const resolvedDevboxTarget = normalizeBaseUrl(devboxBaseUrl || DEFAULT_LOCAL_DEVBOX_PROXY_TARGET);

  return {
    devbox: resolvedDevboxTarget,
    userService: normalizeBaseUrl(userServiceBaseUrl || defaultTarget),
    localUserId: normalizedLocalUserId,
  };
}

export function extractUserIdFromBearerToken(authorizationHeader?: string | string[]) {
  const rawHeader = Array.isArray(authorizationHeader) ? authorizationHeader[0] : authorizationHeader;
  if (!rawHeader) {
    return null;
  }

  const token = rawHeader.match(/^Bearer\s+(.+)$/i)?.[1]?.trim();
  if (!token) {
    return null;
  }

  const payload = parseJwtPayload(token);
  if (!payload || typeof payload !== "object") {
    return null;
  }

  const userId = payload.sub ?? payload.user_id;
  return typeof userId === "string" && userId.trim() ? userId : null;
}

export function createChatDevProxy(targets: ChatDevProxyTargets): Record<string, ProxyOptions> {
  const devboxTarget = normalizeBaseUrl(targets.devbox);
  const userServiceTarget = normalizeBaseUrl(targets.userService);

  return {
    "/api/devbox": {
      target: devboxTarget,
      changeOrigin: true,
      secure: isSecureTarget(devboxTarget),
      configure(proxy) {
        proxy.on("proxyReq", (proxyReq, req) => {
          attachLocalUserId(proxyReq, req, targets.localUserId);
        });
      },
    },
    "/api/user-service": {
      target: userServiceTarget,
      changeOrigin: true,
      secure: isSecureTarget(userServiceTarget),
    },
  };
}

function normalizeBaseUrl(value: string) {
  return value.replace(/\/+$/, "");
}

function isSecureTarget(value: string) {
  return value.startsWith("https://");
}

function attachLocalUserId(
  proxyReq: {
    setHeader: (name: string, value: string) => void;
  },
  req: IncomingMessage,
  fallbackUserId?: string,
) {
  const userId =
    extractUserIdFromBearerToken(req.headers.authorization) ||
    extractUserIdFromHeader(req.headers["x-user-id"]) ||
    fallbackUserId;

  if (userId) {
    proxyReq.setHeader("X-User-Id", userId);
  }
}

function extractUserIdFromHeader(headerValue?: string | string[]) {
  const rawValue = Array.isArray(headerValue) ? headerValue[0] : headerValue;
  return typeof rawValue === "string" && rawValue.trim() ? rawValue : null;
}

function parseJwtPayload(token: string) {
  const parts = token.split(".");
  if (parts.length < 2) {
    return null;
  }

  try {
    const normalizedPayload = parts[1].replace(/-/g, "+").replace(/_/g, "/");
    const paddedPayload = normalizedPayload.padEnd(Math.ceil(normalizedPayload.length / 4) * 4, "=");
    return JSON.parse(Buffer.from(paddedPayload, "base64").toString("utf-8")) as Record<string, unknown>;
  } catch {
    return null;
  }
}
