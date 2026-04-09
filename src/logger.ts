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

// Route uncaught errors through pino so they get timestamps in stderr
process.on('uncaughtException', (err) => {
  logger.fatal({ err }, 'Uncaught exception');
  process.exit(1);
});

process.on('unhandledRejection', (reason) => {
  logger.error({ err: reason }, 'Unhandled rejection');
});
