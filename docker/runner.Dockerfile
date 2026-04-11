FROM ubuntu:24.04

RUN apt-get update && apt-get install -y \
    build-essential ca-certificates curl git openssh-client \
    pkg-config cmake clang libclang-dev libssl-dev \
    protobuf-compiler tmux jq ripgrep rsync unzip xz-utils \
    sudo locales \
    && rm -rf /var/lib/apt/lists/*

# Install GitHub CLI (gh) for PR creation
RUN curl -fsSL https://cli.github.com/packages/githubcli-archive-keyring.gpg \
      -o /usr/share/keyrings/githubcli-archive-keyring.gpg \
    && chmod go+r /usr/share/keyrings/githubcli-archive-keyring.gpg \
    && echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/githubcli-archive-keyring.gpg] https://cli.github.com/packages stable main" \
      > /etc/apt/sources.list.d/github-cli.list \
    && apt-get update && apt-get install -y gh \
    && rm -rf /var/lib/apt/lists/*

RUN arch="$(dpkg --print-architecture)" \
    && case "$arch" in \
      amd64) kubectl_arch=amd64 ;; \
      arm64) kubectl_arch=arm64 ;; \
      *) echo "unsupported kubectl architecture: $arch" >&2; exit 1 ;; \
    esac \
    && kubectl_version="$(curl -fsSL https://dl.k8s.io/release/stable.txt)" \
    && curl -fsSL "https://dl.k8s.io/release/${kubectl_version}/bin/linux/${kubectl_arch}/kubectl" \
      -o /usr/local/bin/kubectl \
    && curl -fsSL "https://dl.k8s.io/release/${kubectl_version}/bin/linux/${kubectl_arch}/kubectl.sha256" \
      -o /tmp/kubectl.sha256 \
    && echo "$(cat /tmp/kubectl.sha256)  /usr/local/bin/kubectl" | sha256sum --check \
    && chmod +x /usr/local/bin/kubectl \
    && rm -f /tmp/kubectl.sha256

# Install Google Cloud CLI and GKE auth plugin for kubectl
# Runners use in-cluster SA + Workload Identity — no credential files needed.
RUN apt-get update && apt-get install -y apt-transport-https gnupg \
    && curl -fsSL https://packages.cloud.google.com/apt/doc/apt-key.gpg \
      | gpg --dearmor -o /usr/share/keyrings/cloud.google.gpg \
    && echo "deb [signed-by=/usr/share/keyrings/cloud.google.gpg] https://packages.cloud.google.com/apt cloud-sdk main" \
      > /etc/apt/sources.list.d/google-cloud-sdk.list \
    && apt-get update && apt-get install -y google-cloud-cli google-cloud-sdk-gke-gcloud-auth-plugin \
    && rm -rf /var/lib/apt/lists/*

RUN curl -fsSL https://deb.nodesource.com/setup_22.x | bash - \
    && apt-get update && apt-get install -y nodejs \
    && rm -rf /var/lib/apt/lists/*

RUN userdel -r ubuntu 2>/dev/null || true \
    && useradd -m -s /bin/bash -u 1000 -G sudo devbox \
    && echo 'devbox ALL=(ALL) NOPASSWD:ALL' >> /etc/sudoers.d/devbox

USER devbox
WORKDIR /home/devbox

RUN curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y --default-toolchain stable
ENV PATH="/home/devbox/.cargo/bin:/home/devbox/.local/bin:$PATH"
ENV CARGO_HOME="/home/devbox/.cargo"
ENV OPENSSL_DIR=/usr
ENV OPENSSL_INCLUDE_DIR=/usr/include
ENV OPENSSL_LIB_DIR=/usr/lib/x86_64-linux-gnu
ENV PROTOC=/usr/bin/protoc
ENV CC=/usr/bin/clang
ENV CXX=/usr/bin/clang++
ENV LIBCLANG_PATH=/usr/lib/llvm-18/lib
ENV PKG_CONFIG_PATH=/usr/lib/x86_64-linux-gnu/pkgconfig

USER root
RUN npm install -g @anthropic-ai/claude-code
WORKDIR /app
COPY --chown=devbox:devbox container/agent-runner/package*.json ./
RUN npm ci
COPY --chown=devbox:devbox container/agent-runner/ ./
RUN npm run build

COPY --chown=devbox:devbox container/entrypoint.sh /app/entrypoint.sh
COPY --chown=devbox:devbox container/gh-wrapper.sh /usr/local/bin/gh
RUN chmod +x /app/entrypoint.sh \
    && chmod +x /usr/local/bin/gh \
    && mkdir -p /workspace/group /workspace/global /workspace/bootstrap /workspace/ipc/messages /workspace/ipc/tasks /workspace/ipc/input \
    && chown -R devbox:devbox /app /workspace

USER devbox
WORKDIR /workspace/group
ENTRYPOINT ["/app/entrypoint.sh"]
