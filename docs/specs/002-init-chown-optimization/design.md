# Spec 002: Eliminate init-container `chown -R` bottleneck

**Status**: Implemented
**Author**: nick
**Date**: 2026-03-12

## Problem

Every runner pod starts with an init container that runs:

```
chown -R 1000:1000 /workspace/group
chown -R 1000:1000 /home/devbox/.claude
chown -R 1000:1000 /workspace/ipc
```

On first session this is fast (empty directories). On subsequent sessions
the `/workspace/group` directory contains all previously cloned repos with
full git history. On NFS (Filestore), `chown -R` issues a stat + chown
syscall per file over the network, causing init times to grow linearly
with accumulated data. A session with 3 repos (~75 MB, tens of thousands
of small `.git/objects` files) takes over 60 seconds in init.

Removing the `-R` flag breaks new sessions because the controller creates
subdirectories (e.g. `workspace/`, `.claude/`, `ipc/`) as root, and the
runner (uid 1000) cannot write into them.

## Sequence Diagram: Current Flow

```
Controller (root)              Init Container (root)         Runner (uid 1000)
      |                               |                            |
      |  mkdirSync(sessionDir)        |                            |
      |  mkdirSync(workspace/)        |                            |
      |  mkdirSync(.claude/)          |                            |
      |  mkdirSync(ipc/messages/)     |                            |
      |  mkdirSync(ipc/tasks/)        |                            |
      |  mkdirSync(ipc/input/)        |                            |
      |  writeFileSync(settings.json) |                            |
      |  cpSync(skills/)              |                            |
      |  writeFileSync(seed-manifest) |                            |
      |  writeFileSync(CLAUDE.md)     |                            |
      |                               |                            |
      |  --- All files owned by root:root ---                      |
      |                               |                            |
      |  Create Pod ----------------->|                            |
      |                               |                            |
      |                    chown -R 1000:1000                      |
      |                    /workspace/group    <--- SLOW on NFS    |
      |                    (traverses ALL files                    |
      |                     including old repos)                   |
      |                               |                            |
      |                    chown -R 1000:1000                      |
      |                    /home/devbox/.claude                    |
      |                               |                            |
      |                    chown -R 1000:1000                      |
      |                    /workspace/ipc                          |
      |                               |                            |
      |                               |  Start ------------------->|
      |                               |                            |
      |                               |            entrypoint.sh   |
      |                               |            git clone repos |
      |                               |            (if first seed) |
      |                               |            node agent      |
```

### Why the controller creates files as root

The controller deployment runs as root (no `securityContext.runAsUser` set
on the controller container). All `fs.mkdirSync`, `fs.writeFileSync`, and
`fs.cpSync` calls in `buildVolumeMounts()` therefore produce root-owned
files on the PVC.

### Why the runner needs uid 1000

The runner image creates a `devbox` user (uid 1000) and sets
`USER devbox` in the Dockerfile. The pod spec passes
`securityContext.runAsUser: 1000` when the controller itself is not root
(Docker Compose path), but on Kubernetes the controller IS root, so
`runtimeUser` is `undefined` and the container falls back to the
Dockerfile `USER devbox`.

## Proposed Fix: Controller creates files as uid 1000

### Sequence Diagram: Fixed Flow

```
Controller (root)                                   Runner (uid 1000)
      |                                                    |
      |  mkdirSync(sessionDir, uid=1000)                   |
      |  mkdirSync(workspace/, uid=1000)                   |
      |  mkdirSync(.claude/, uid=1000)                     |
      |  mkdirSync(ipc/messages/, uid=1000)                |
      |  mkdirSync(ipc/tasks/, uid=1000)                   |
      |  mkdirSync(ipc/input/, uid=1000)                   |
      |  writeFile(settings.json, uid=1000)                |
      |  cpSync(skills/, uid=1000)                         |
      |  writeFile(seed-manifest, uid=1000)                |
      |  writeFile(CLAUDE.md, uid=1000)                    |
      |                                                    |
      |  --- All files owned by 1000:1000 ---              |
      |                                                    |
      |  Create Pod (NO init container) ------------------>|
      |                                                    |
      |                                     entrypoint.sh  |
      |                                     git clone      |
      |                                     node agent     |
```

### Implementation

The controller runs as root and can freely set file ownership. After each
`mkdirSync` / `writeFileSync` / `cpSync`, call `chownSync` to set
ownership to 1000:1000. This is fast because it only touches the files
the controller just created (a handful of directories and config files),
not the entire repo tree.

**Step 1**: Add a helper that creates a directory and sets ownership:

```typescript
const RUNNER_UID = 1000;
const RUNNER_GID = 1000;

function mkdirOwnedSync(dirPath: string): void {
  fs.mkdirSync(dirPath, { recursive: true });
  fs.chownSync(dirPath, RUNNER_UID, RUNNER_GID);
}

function writeFileOwnedSync(filePath: string, data: string): void {
  fs.writeFileSync(filePath, data);
  fs.chownSync(filePath, RUNNER_UID, RUNNER_GID);
}

function cpOwnedSync(src: string, dst: string): void {
  fs.cpSync(src, dst, { recursive: true });
  // chown the copied tree — this is small (just skill files)
  chownRecursiveSync(dst, RUNNER_UID, RUNNER_GID);
}
```

**Step 2**: Replace all `fs.mkdirSync` / `fs.writeFileSync` / `fs.cpSync`
calls in `buildVolumeMounts()` with the owned variants.

**Step 3**: Remove the init container from `K8sRuntime.spawn()`.

### Edge Cases

1. **Returning sessions**: Directories already exist and are already
   owned by 1000:1000 from the previous runner. `mkdirSync` with
   `recursive: true` is a no-op when the directory exists. The
   `chownSync` on an already-1000 directory is a single fast NFS call
   (not recursive).

2. **`syncStaticSessionConfig` and `cpSync(skills)`**: These write
   files as root. They need to chown after writing. The skills
   directory is small (a few files), so recursive chown here is fine.

3. **`writeFileSync(settings.json)`**: Only written if it doesn't exist
   yet, but already owned by root. Needs chown.

4. **Docker Compose runtime**: The Docker runtime uses `--user` flag
   instead of init containers, and the controller may not run as root
   locally. The helper should be a no-op when `process.getuid() !== 0`
   to avoid permission errors in local dev.

### Alternatives Considered

| Approach | Why rejected |
|----------|-------------|
| `chown -R` (current) | O(n) on NFS, gets slower as repos grow |
| `chown` without `-R` | Misses controller-created subdirectories |
| `find -user 0 -exec chown` | Still traverses entire tree to find root-owned files |
| `fsGroup` in pod securityContext | Kubernetes applies fsGroup via `chown -R` on mount, same problem |
| Run controller as uid 1000 | Would break PVC access when controller needs root for other ops |
| Run runner as root | Security regression, violates least-privilege |

### Migration

The init container should be kept for one release as a safety net, but
changed to non-recursive `chown` on only the mount points. Once we
confirm the controller-side chown is working correctly in production,
remove the init container entirely.

## Impact

- Runner pod startup reduced by 30-60+ seconds for returning sessions
- Eliminates O(n) NFS overhead that grows with repo history
- Removes the `busybox:1.36` init container image dependency
- No behavioral change for the runner or entrypoint
