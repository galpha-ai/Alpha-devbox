FROM node:22-slim

RUN apt-get update \
  && apt-get install -y --no-install-recommends \
    docker.io \
    git \
    openssh-client \
    python3 \
    make \
    g++ \
  && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY package*.json ./
RUN npm ci --omit=dev --ignore-scripts \
  && npm rebuild better-sqlite3

COPY dist/ ./dist/
COPY container/skills/ ./container/skills/
COPY container/agent-runner/src/ ./container/agent-runner/src/
COPY agents/ ./agents/

ENTRYPOINT ["node", "dist/index.js"]
