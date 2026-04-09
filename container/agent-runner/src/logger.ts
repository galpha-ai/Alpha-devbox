import pino from 'pino';

// Use structured JSON logging by default
// Set PINO_PRETTY=1 for human-readable output in local development
const usePretty = process.env.PINO_PRETTY === '1';

export const logger = pino({
  level: process.env.LOG_LEVEL || 'info',
  ...(usePretty
    ? { transport: { target: 'pino-pretty', options: { colorize: true } } }
    : {}),
});
