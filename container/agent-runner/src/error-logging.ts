const REDACTED = '[REDACTED]';
const SENSITIVE_KEY_PATTERN =
  /(?:api[-_]?key|token|secret|authorization|cookie|password)/i;

export function collectSecretValues(
  secrets?: Record<string, string>,
): string[] {
  return Object.values(secrets || {}).filter(
    (value): value is string => typeof value === 'string' && value.length > 0,
  );
}

function redactSecretStrings(value: string, secretValues: string[]): string {
  let redacted = value;
  for (const secret of secretValues) {
    redacted = redacted.split(secret).join(REDACTED);
  }
  return redacted;
}

export function sanitizeForLogging(
  value: unknown,
  secretValues: string[],
  seen = new WeakSet<object>(),
): unknown {
  if (typeof value === 'string') {
    return redactSecretStrings(value, secretValues);
  }
  if (
    value === null ||
    typeof value === 'number' ||
    typeof value === 'boolean'
  ) {
    return value;
  }
  if (typeof value === 'bigint') {
    return value.toString();
  }
  if (value === undefined) {
    return '[undefined]';
  }
  if (typeof value === 'function' || typeof value === 'symbol') {
    return String(value);
  }
  if (value instanceof Error) {
    const errorLike: Record<string, unknown> = {
      name: value.name,
      message: value.message,
      stack: value.stack,
    };
    if (value.cause !== undefined) {
      errorLike.cause = sanitizeForLogging(value.cause, secretValues, seen);
    }
    for (const key of Object.getOwnPropertyNames(value)) {
      if (key in errorLike) continue;
      errorLike[key] = sanitizeForLogging(
        (value as unknown as Record<string, unknown>)[key],
        secretValues,
        seen,
      );
    }
    return errorLike;
  }
  if (Array.isArray(value)) {
    return value.map((entry) => sanitizeForLogging(entry, secretValues, seen));
  }
  if (typeof value === 'object') {
    if (seen.has(value)) {
      return '[Circular]';
    }
    seen.add(value);
    const sanitized: Record<string, unknown> = {};
    for (const [key, entry] of Object.entries(
      value as Record<string, unknown>,
    )) {
      sanitized[key] = SENSITIVE_KEY_PATTERN.test(key)
        ? REDACTED
        : sanitizeForLogging(entry, secretValues, seen);
    }
    seen.delete(value);
    return sanitized;
  }
  return String(value);
}

export function formatForLog(value: unknown, secretValues: string[]): string {
  const sanitized = sanitizeForLogging(value, secretValues);
  return typeof sanitized === 'string'
    ? sanitized
    : JSON.stringify(sanitized, null, 2);
}
