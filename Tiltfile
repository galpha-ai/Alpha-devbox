# -*- mode: Python -*-

# Suppress unused image warning for runner (dynamically created by controller)
update_settings(suppress_unused_image_warnings=["devbox-runner:latest"])

# Load Kubernetes YAML
k8s_yaml(kustomize('k8s/local'))

# Build controller image
docker_build(
  'devbox-controller:latest',
  '.',
  dockerfile='docker/controller.Dockerfile',
  live_update=[
    sync('./src', '/app/src'),
    sync('./package.json', '/app/package.json'),
    sync('./config.local.yaml', '/app/config.local.yaml'),
    run('cd /app && npm install', trigger=['./package.json']),
  ]
)

# Build runner image
docker_build(
  'devbox-runner:latest',
  '.',
  dockerfile='docker/runner.Dockerfile',
  live_update=[
    sync('./container/agent-runner/src', '/app/src'),
    sync('./container/agent-runner/package.json', '/app/package.json'),
    run('cd /app && npm install', trigger=['./container/agent-runner/package.json']),
  ]
)

# Configure controller resource
k8s_resource(
  'devbox-controller',
  port_forwards=['8080:8080'],
  labels=['core'],
  resource_deps=['k8s-secrets']  # Wait for secrets before starting
)

# Ensure using OrbStack context
local_resource(
  'k8s-context',
  cmd='kubectl config use-context orbstack',
  labels=['infra']
)

# Create secrets from env
local_resource(
  'k8s-secrets',
  cmd='''
    kubectl create secret generic devbox-agent-secrets \
      --from-literal=telegram-bot-token="${TELEGRAM_BOT_TOKEN:-}" \
      --from-literal=slack-bot-token="${SLACK_BOT_TOKEN:-}" \
      --from-literal=slack-app-token="${SLACK_APP_TOKEN:-}" \
      --from-literal=anthropic-api-key="${ANTHROPIC_API_KEY:-}" \
      --from-literal=github-token="${GITHUB_TOKEN:-}" \
      --dry-run=client -o yaml | kubectl apply -f -
  ''',
  deps=[],
  labels=['infra']
)
