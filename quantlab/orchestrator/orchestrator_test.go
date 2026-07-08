package main

import (
	"bytes"
	"context"
	"encoding/json"
	"os"
	"path/filepath"
	"strings"
	"testing"
	"time"
)

// writeScript writes an executable /bin/sh script and returns its path.
func writeScript(t *testing.T, path, body string) string {
	t.Helper()
	if err := os.WriteFile(path, []byte("#!/bin/sh\n"+body+"\n"), 0o755); err != nil {
		t.Fatal(err)
	}
	return path
}

// runPlan marshals p to <dir>/plan.json, loads it back through LoadPlan
// (so defaults apply), runs it, and returns the summary plus final status.
func runPlan(t *testing.T, dir string, p Plan, timeout time.Duration) (Summary, map[string]TaskStatus) {
	t.Helper()
	raw, _ := json.Marshal(p)
	planPath := filepath.Join(dir, "plan.json")
	if err := os.WriteFile(planPath, raw, 0o644); err != nil {
		t.Fatal(err)
	}
	loaded, err := LoadPlan(planPath)
	if err != nil {
		t.Fatalf("LoadPlan: %v", err)
	}
	o := &Orchestrator{Plan: loaded, PlanPath: planPath, Parallel: 4, TaskTimeout: timeout}
	sum, err := o.Run(context.Background())
	if err != nil {
		t.Fatalf("Run: %v", err)
	}
	raw, err = os.ReadFile(filepath.Join(dir, "status.json"))
	if err != nil {
		t.Fatalf("status.json missing: %v", err)
	}
	var sf statusFile
	if err := json.Unmarshal(raw, &sf); err != nil {
		t.Fatalf("status.json is not valid JSON: %v", err)
	}
	byID := map[string]TaskStatus{}
	for _, ts := range sf.Tasks {
		byID[ts.ID] = ts
	}
	return sum, byID
}

func TestTopoOrderDiamond(t *testing.T) {
	p := Plan{Tasks: []Task{
		{ID: "d", DependsOn: []string{"b", "c"}},
		{ID: "c", DependsOn: []string{"a"}},
		{ID: "b", DependsOn: []string{"a"}},
		{ID: "a"},
	}}
	order, err := TopoOrder(p)
	if err != nil {
		t.Fatal(err)
	}
	want := []string{"a", "b", "c", "d"}
	if strings.Join(order, ",") != strings.Join(want, ",") {
		t.Fatalf("order = %v, want %v", order, want)
	}
	// Cycle must be rejected.
	cyc := Plan{Tasks: []Task{{ID: "x", DependsOn: []string{"y"}}, {ID: "y", DependsOn: []string{"x"}}}}
	if _, err := TopoOrder(cyc); err == nil {
		t.Fatal("expected cycle error, got nil")
	}
	// Unknown dependency must be rejected.
	bad := Plan{Tasks: []Task{{ID: "x", DependsOn: []string{"ghost"}}}}
	if _, err := TopoOrder(bad); err == nil {
		t.Fatal("expected unknown-dependency error, got nil")
	}
}

func TestRetryThenPassWithPrevFailureEnv(t *testing.T) {
	dir := t.TempDir()
	marker := filepath.Join(dir, "verify-ran-once")
	prevLog := filepath.Join(dir, "prevfail.log")
	exec := writeScript(t, filepath.Join(dir, "exec.sh"),
		`printf '[%s]' "$QL_PREV_FAILURE" >> `+prevLog)
	// Fails on first invocation (creates marker), passes on the second.
	verify := writeScript(t, filepath.Join(dir, "verify.sh"),
		`if [ -f `+marker+` ]; then exit 0; fi
touch `+marker+`
echo "verify failed: rows mismatch"
exit 1`)
	p := Plan{Tasks: []Task{{ID: "flaky", Layer: "L2", ExecCmd: exec, VerifyCmd: verify}}}
	sum, st := runPlan(t, dir, p, time.Minute)
	if st["flaky"].State != "done" || st["flaky"].Attempts != 2 {
		t.Fatalf("flaky: state=%s attempts=%d, want done/2", st["flaky"].State, st["flaky"].Attempts)
	}
	if sum.Done != 1 || sum.Total != 1 {
		t.Fatalf("summary = %+v, want 1/1 done", sum)
	}
	log, _ := os.ReadFile(prevLog)
	// First attempt: empty env. Second attempt: env carries the verify output.
	if !strings.HasPrefix(string(log), "[]") || !strings.Contains(string(log), "rows mismatch") {
		t.Fatalf("QL_PREV_FAILURE not propagated to retry, log = %q", log)
	}
}

func TestEscalationAndDependencyBlocking(t *testing.T) {
	dir := t.TempDir()
	p := Plan{Tasks: []Task{
		{ID: "bad", ExecCmd: "true", VerifyCmd: "echo unacceptable; exit 1"}, // default max_attempts=2
		{ID: "child", ExecCmd: "true", VerifyCmd: "true", DependsOn: []string{"bad"}},
		{ID: "indep", ExecCmd: "true", VerifyCmd: "true"},
	}}
	sum, st := runPlan(t, dir, p, time.Minute)
	if st["bad"].State != "escalate" || st["bad"].Attempts != 2 {
		t.Fatalf("bad: state=%s attempts=%d, want escalate/2", st["bad"].State, st["bad"].Attempts)
	}
	if !strings.Contains(st["bad"].LastVerifyOutput, "unacceptable") {
		t.Fatalf("last_verify_output = %q, want verify output", st["bad"].LastVerifyOutput)
	}
	if st["child"].State != "failed" || !strings.Contains(st["child"].LastVerifyOutput, "bad") {
		t.Fatalf("child: %+v, want failed + blocked-by-bad note", st["child"])
	}
	if st["indep"].State != "done" {
		t.Fatalf("indep: state=%s, want done (must continue past escalation)", st["indep"].State)
	}
	if sum.Done != 1 || sum.Escalate != 1 || sum.Failed != 1 {
		t.Fatalf("summary = %+v, want done=1 escalate=1 failed=1", sum)
	}
}

func TestStatusFileShapeAndAtomicity(t *testing.T) {
	dir := t.TempDir()
	statusPath := filepath.Join(dir, "status.json")
	captured := filepath.Join(dir, "captured")
	// exec proves status.json already reports this task as running and is
	// parseable JSON at the moment exec runs (i.e. never a half-written file).
	exec := `grep '"state": "running"' ` + statusPath + ` > ` + captured
	p := Plan{Tasks: []Task{{ID: "solo", Layer: "L4", ExecCmd: exec, VerifyCmd: "true"}}}
	_, st := runPlan(t, dir, p, time.Minute)
	s := st["solo"]
	if s.State != "done" || s.Attempts != 1 || s.Layer != "L4" {
		t.Fatalf("solo = %+v, want done/1/L4", s)
	}
	if s.StartedAt == "" || s.FinishedAt == "" {
		t.Fatalf("timestamps missing: %+v", s)
	}
	if got, _ := os.ReadFile(captured); !strings.Contains(string(got), "running") {
		t.Fatalf("status.json did not show running state mid-exec: %q", got)
	}
	// Truncation contract.
	if len(s.LastVerifyOutput) > 2000 {
		t.Fatalf("last_verify_output exceeds 2000 chars: %d", len(s.LastVerifyOutput))
	}
	// Atomic write must not leave temp files behind.
	if tmps, _ := filepath.Glob(filepath.Join(dir, ".status*")); len(tmps) != 0 {
		t.Fatalf("temp files left behind: %v", tmps)
	}
}

func TestTaskTimeoutEscalates(t *testing.T) {
	dir := t.TempDir()
	p := Plan{Tasks: []Task{{ID: "slow", ExecCmd: "sleep 5", VerifyCmd: "true", MaxAttempts: 1}}}
	start := time.Now()
	_, st := runPlan(t, dir, p, 200*time.Millisecond)
	if st["slow"].State != "escalate" {
		t.Fatalf("slow: state=%s, want escalate", st["slow"].State)
	}
	if time.Since(start) > 3*time.Second {
		t.Fatal("timeout not enforced")
	}
}

func TestDryRunPrintsTopologicalOrder(t *testing.T) {
	p := Plan{Tasks: []Task{
		{ID: "d", Layer: "L4", DependsOn: []string{"b", "c"}},
		{ID: "c", Layer: "L2", DependsOn: []string{"a"}},
		{ID: "b", Layer: "L2", DependsOn: []string{"a"}},
		{ID: "a", Layer: "L1"},
	}}
	o := &Orchestrator{Plan: p}
	var buf bytes.Buffer
	if err := o.DryRun(&buf); err != nil {
		t.Fatal(err)
	}
	out := buf.String()
	for _, want := range []string{"1. a", "2. b", "3. c", "4. d", "[L4]", "deps: b, c"} {
		if !strings.Contains(out, want) {
			t.Fatalf("dry-run output missing %q:\n%s", want, out)
		}
	}
}

func TestSamplePlanRuns(t *testing.T) {
	raw, err := os.ReadFile("testdata/sample-plan.json")
	if err != nil {
		t.Fatal(err)
	}
	dir := t.TempDir()
	planPath := filepath.Join(dir, "plan.json")
	if err := os.WriteFile(planPath, raw, 0o644); err != nil {
		t.Fatal(err)
	}
	plan, err := LoadPlan(planPath)
	if err != nil {
		t.Fatal(err)
	}
	o := &Orchestrator{Plan: plan, PlanPath: planPath, Parallel: 4, TaskTimeout: time.Minute}
	sum, err := o.Run(context.Background())
	if err != nil {
		t.Fatal(err)
	}
	if sum.Done != sum.Total || sum.Total == 0 {
		t.Fatalf("sample plan: %+v, want all done", sum)
	}
}
