"""export_logs.py — check the harness's sub-agent results into the repository.

Copies, for every Workflow run of this session, the journal (each agent's structured return value)
and the per-agent metadata into research/riemann-rmt/overnight/fable/harness_logs/<run>/, and writes
INDEX.md with one row per agent (label, status, model, tokens if recorded). Full transcripts stay in
the session directory; the journal carries every proposer/refuter/repair verdict verbatim.
"""
import json, os, shutil, glob, sys
ROOTS = ["/root/.claude/projects/-home-user-Alpha-devbox/00b3b5f7-f917-5641-a9be-c6a8f38f5cd7/subagents/workflows",
         "/root/.claude/projects/-home-user-Alpha-devbox-research-riemann-rmt-overnight-fable/00b3b5f7-f917-5641-a9be-c6a8f38f5cd7/subagents/workflows"]
OUT = os.path.dirname(os.path.abspath(__file__))
rows = []
for root in ROOTS:
    for run in sorted(glob.glob(os.path.join(root, "wf_*"))):
        name = os.path.basename(run)
        dst = os.path.join(OUT, name); os.makedirs(dst, exist_ok=True)
        j = os.path.join(run, "journal.jsonl")
        if os.path.exists(j):
            shutil.copy(j, os.path.join(dst, "journal.jsonl"))
        for m in glob.glob(os.path.join(run, "agent-*.meta.json")):
            shutil.copy(m, dst)
            try:
                d = json.load(open(m))
            except Exception:
                d = {}
            rows.append((name, os.path.basename(m).replace(".meta.json", ""),
                         str(d.get("label", d.get("description", "")))[:60],
                         str(d.get("status", "")), str(d.get("model", ""))))
with open(os.path.join(OUT, "INDEX.md"), "w") as f:
    f.write("# Harness log index\n\n| run | agent | label | status | model |\n|---|---|---|---|---|\n")
    for r in rows:
        f.write("| " + " | ".join(r) + " |\n")
print(f"{len(rows)} agent records exported")
