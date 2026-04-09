# Agent Secret Mounts

This runbook describes how to expose static files, such as kubeconfigs, to runner containers with `secretMounts` in `seed.yaml`.

## When to use this

Use `secretMounts` for long-lived infrastructure credentials that should be mounted as files inside the runner container. Do not use this for per-run secrets that already flow through `input.json`.

## 1. Create the Kubernetes Secret

Create a Secret in the same namespace where runner pods start. Store the kubeconfig under the key `config` so it lands at `/home/devbox/.kube/config` inside the container.

```bash
KUBECONFIG=/home/youruser/.kube/your-cluster.yaml \
kubectl -n devbox-agent-staging create secret generic quant-dev-kubeconfig \
  --from-file=config=/home/youruser/.kube/your-cluster.yaml
```

If your local kubeconfig path differs, use the value from `tools.md`. If `tools.md` does not exist yet, create it from `tools.example.md` and record the path there before using this workflow.

## 2. Declare the mount in `seed.yaml`

Add a `secretMounts` entry to the agent definition. `secretName` is the Kubernetes Secret name, `mountPath` is the in-container destination, and `hostPath` is the Docker fallback for local runs.

```yaml
secretMounts:
  - secretName: quant-dev-kubeconfig
    mountPath: /home/devbox/.kube
    hostPath: /home/youruser/.kube/quant-dev
```

Kubernetes mounts the Secret as a read-only volume at `/home/devbox/.kube`. Docker bind-mounts the local directory at the same path, also read-only.

## 3. Prepare the Docker fallback

Docker expects `hostPath` to be a directory whose contents should appear at `mountPath`. For kubeconfigs, create a directory that contains a single `config` file:

```bash
mkdir -p /home/youruser/.kube/quant-dev
cp /home/youruser/.kube/your-cluster.yaml /home/youruser/.kube/quant-dev/config
```

If you use a different kubeconfig file locally, replace `/home/youruser/.kube/your-cluster.yaml` with the value from `tools.md`.

## 4. Verify inside the runner

After starting a runner for the agent, verify the file is present:

```bash
ls -l /home/devbox/.kube
KUBECONFIG=/home/devbox/.kube/config kubectl config current-context
```

## Example

- Agent: `agents/example/seed.yaml`
- Secret: `example-kubeconfig`
- Mount path: `/home/devbox/.kube`
- Expected file inside container: `/home/devbox/.kube/config`
- Docker fallback directory: `~/.kube/example`
