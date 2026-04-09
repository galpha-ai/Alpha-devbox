# Local Kubernetes Development with Tilt

**Recommended for complete development and testing**

## Why Choose K8s Development Environment

### Core Benefits

1. **Test Production Features**
   - ✅ Controller dynamically creates Runner Pods (core functionality)
   - ✅ RBAC validation (ServiceAccount, Role, RoleBinding)
   - ✅ K8s PVC persistence behavior
   - ✅ Pod lifecycle management

2. **Development Efficiency**
   - ✅ Hot reload (5s vs 2-5min manual restart)
   - ✅ Unified log aggregation (controller + multiple runner pods)
   - ✅ Automated environment setup (secrets, context switching)
   - ✅ Visual resource monitoring (build times, dependencies)

3. **Environment Consistency**
   - ✅ Local K8s = Production K8s (eliminate "works locally, fails in prod")
   - ✅ Same YAML configs (kustomize base + overlays)
   - ✅ Same container runtime behavior

### vs Docker Compose

| Feature | Tilt + K8s | Docker Compose |
|---------|-----------|----------------|
| **Dynamic Pod creation** | ✅ Full support | ❌ Docker containers only |
| **RBAC testing** | ✅ Full support | ❌ Not available |
| **PVC behavior** | ✅ K8s PVC | ❌ Docker volume (different) |
| **Hot reload** | ✅ 5s | ❌ Manual restart |
| **Log aggregation** | ✅ Unified UI | ❌ Multiple terminals |
| **Environment parity** | ✅ High | ⚠️ Medium |
| **Startup time** | ~10s | ~5s |
| **Memory usage** | ~1GB | ~500MB |

**Conclusion**: Compose for quick controller logic testing, K8s for complete development and testing.

---

## Prerequisites

```bash
# Install OrbStack (includes Docker + Kubernetes)
brew install orbstack

# Install Tilt
brew install tilt

# Enable Kubernetes in OrbStack
# Open OrbStack → Settings → Kubernetes → Enable
```

## Quick Start

```bash
# 1. Create data directory
sudo mkdir -p /data/devbox-agent
sudo chown "$(id -u):$(id -g)" /data/devbox-agent

# 2. Verify OrbStack K8s is running
just k8s-check

# 3. Set environment variables
export TELEGRAM_BOT_TOKEN="your-token"
export ANTHROPIC_API_KEY="your-key"
export GITHUB_TOKEN="your-token"

# 4. Start Tilt (builds images, deploys, watches for changes)
just dev-k8s
```

Tilt UI will open at http://localhost:10350

## Tilt Features Explained

### 1. Hot Reload (Live Update)
- Edit `src/**/*.ts` → auto-sync to controller pod (5s)
- Edit `container/agent-runner/src/**/*.ts` → auto-sync to runner pods (5s)
- Edit `package.json` → auto `npm install` + restart

### 2. Log Aggregation
Tilt UI shows all resource logs in one place:
- devbox-controller (long-running)
- runner-xxx (dynamically created pods)
- k8s-secrets, k8s-context (initialization tasks)

### 3. Resource Dependency Orchestration
```python
# Tiltfile automatically handles startup order
k8s-context → k8s-secrets → devbox-controller → runner pods
```

### 4. Port Forwarding
Auto-forward controller ports:
- http://localhost:8080/health (health check)

### 5. Resource Grouping
Tilt UI groups by labels:
- **infra**: k8s-context, k8s-secrets
- **core**: devbox-controller

---

## Development Workflow

### Code Changes
- Edit `src/**/*.ts` → Controller auto-rebuilds
- Edit `container/agent-runner/src/**/*.ts` → Runner auto-rebuilds
- Changes sync to pods without full restart (live_update)

### View Logs
- Tilt UI: http://localhost:10350
- CLI: `tilt logs devbox-controller`
- kubectl: `kubectl logs -l app=devbox-agent -f`

### Debug Runner Pods
```bash
# List all pods (including dynamically created runners)
kubectl get pods

# View runner logs
kubectl logs <runner-pod-name>

# Exec into runner
kubectl exec -it <runner-pod-name> -- /bin/bash
```

### Clean Up
```bash
# Stop Tilt (Ctrl+C in terminal)

# Remove data
just clean-data

# Full cleanup
just clean-all
```

## Architecture

```
Local Machine
├── OrbStack K8s
│   ├── devbox-controller pod
│   │   └── spawns runner pods dynamically via K8s API
│   ├── devbox-data-local PVC
│   └── RBAC (ServiceAccount, Role, RoleBinding)
├── Tilt
│   ├── watches src/ and container/
│   ├── builds images on change
│   └── syncs code to pods (live_update)
└── /data/devbox-agent (host volume)
    └── mounted into PVC
```

## Differences from Production

| Aspect | Local (OrbStack) | Production (GKE/k3s) |
|--------|-----------------|----------------------|
| Storage | local-path | GCE PD / hostPath |
| Image Pull | Never (local build) | IfNotPresent |
| Registry | Local | GCR / Docker Hub |
| Namespace | default | devbox-agent |

## Troubleshooting

### OrbStack K8s not running
```bash
# Check context
kubectl config current-context

# Should output: orbstack
# If not, enable K8s in OrbStack settings
```

### Images not found
```bash
# Tilt builds images automatically
# If manual build needed:
just build-images
```

### PVC not mounting
```bash
# Ensure host directory exists
sudo mkdir -p /data/devbox-agent
sudo chown "$(id -u):$(id -g)" /data/devbox-agent

# Check PVC status
kubectl get pvc
kubectl describe pvc devbox-data-local
```

### Runner pods fail to start
```bash
# Check RBAC
kubectl get serviceaccount devbox-runner
kubectl get role devbox-runner-role
kubectl get rolebinding devbox-runner-binding

# Check controller logs
kubectl logs -l app=devbox-agent
```

## What Tilt Provides Beyond Hot Reload

### 1. Dependency Orchestration
Automatically manages resource startup order and dependencies.

### 2. Local Resources
Runs host commands (kubectl, secret creation) as part of the dev workflow.

### 3. Unified Dashboard
Single UI for logs, build status, resource health, and port forwards.

### 4. Build Optimization
- Incremental builds (only changed layers)
- Conditional execution (npm install only when package.json changes)
- Parallel builds (controller + runner simultaneously)

### 5. Extensions Ecosystem
- helm_remote: Deploy Helm charts
- restart_process: Process-level hot reload
- git_resource: Watch git repo changes

### 6. CI Integration
```bash
# Local development
tilt up

# CI validation (non-interactive)
tilt ci
```

See [Tilt documentation](https://docs.tilt.dev/) for advanced features.

