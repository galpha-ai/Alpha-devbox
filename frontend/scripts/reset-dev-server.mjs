import fs from "node:fs";
import path from "node:path";
import process from "node:process";
import { execSync } from "node:child_process";

const repoRoot = path.resolve(process.cwd());
const markers = [
  path.join(repoRoot, "node_modules", ".bin", "vite"),
  path.join(repoRoot, "node_modules", "@esbuild"),
];

function listProcesses() {
  const output = execSync("ps -axo pid=,command=", { encoding: "utf8" });
  return output
    .split("\n")
    .map((line) => line.trim())
    .filter(Boolean)
    .map((line) => {
      const match = line.match(/^(\d+)\s+(.*)$/);
      if (!match) return null;
      return {
        pid: Number(match[1]),
        command: match[2],
      };
    })
    .filter(Boolean);
}

const currentPid = process.pid;
for (const proc of listProcesses()) {
  if (!proc || proc.pid === currentPid) continue;
  if (!markers.some((marker) => proc.command.includes(marker))) continue;
  if (!proc.command.includes(repoRoot)) continue;

  try {
    process.kill(proc.pid, "SIGTERM");
  } catch {}
}

for (const relPath of ["node_modules/.vite", "node_modules/.vite-temp"]) {
  fs.rmSync(path.join(repoRoot, relPath), { recursive: true, force: true });
}

console.log("reset-dev-server: cleaned scoped vite/esbuild processes and cache");
