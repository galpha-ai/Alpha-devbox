// Package main implements a plan-driven agent-loop orchestrator: it
// topologically orders tasks from a plan.json, runs them with a bounded
// worker pool, and drives a dispatch -> verify -> retry/escalate loop per
// task. State is persisted atomically to status.json after every change.
package main

import (
	"context"
	"encoding/json"
	"errors"
	"fmt"
	"io"
	"os"
	"os/exec"
	"path/filepath"
	"sort"
	"strings"
	"sync"
	"syscall"
	"time"
)

const (
	defaultMaxAttempts = 2
	outputTruncateLen  = 2000
	prevFailureEnvVar  = "QL_PREV_FAILURE"
)

// Task is one node of the plan DAG.
type Task struct {
	ID          string   `json:"id"`
	Layer       string   `json:"layer"`
	Objective   string   `json:"objective"`
	ExecCmd     string   `json:"exec_cmd"`
	VerifyCmd   string   `json:"verify_cmd"`
	MaxAttempts int      `json:"max_attempts"`
	DependsOn   []string `json:"depends_on"`
}

// Plan is the top-level plan.json document.
type Plan struct {
	Tasks []Task `json:"tasks"`
}

// TaskStatus is the per-task record persisted to status.json.
type TaskStatus struct {
	ID               string `json:"id"`
	Layer            string `json:"layer"`
	State            string `json:"state"` // pending|running|done|failed|escalate
	Attempts         int    `json:"attempts"`
	LastVerifyOutput string `json:"last_verify_output"`
	StartedAt        string `json:"started_at,omitempty"`
	FinishedAt       string `json:"finished_at,omitempty"`
}

type statusFile struct {
	Plan      string       `json:"plan"`
	UpdatedAt string       `json:"updated_at"`
	Tasks     []TaskStatus `json:"tasks"` // sorted by id
}

// Summary is the end-of-run tally.
type Summary struct{ Total, Done, Failed, Escalate int }

func (s Summary) String() string {
	return fmt.Sprintf("plan finished: %d/%d done, %d escalate, %d failed",
		s.Done, s.Total, s.Escalate, s.Failed)
}

// LoadPlan reads and validates a plan file, applying defaults.
func LoadPlan(path string) (Plan, error) {
	raw, err := os.ReadFile(path)
	if err != nil {
		return Plan{}, err
	}
	var p Plan
	if err := json.Unmarshal(raw, &p); err != nil {
		return Plan{}, fmt.Errorf("parsing %s: %w", path, err)
	}
	for i := range p.Tasks {
		t := &p.Tasks[i]
		if t.MaxAttempts <= 0 {
			t.MaxAttempts = defaultMaxAttempts
		}
		if t.ExecCmd == "" || t.VerifyCmd == "" {
			return Plan{}, fmt.Errorf("task %q: exec_cmd and verify_cmd are required", t.ID)
		}
	}
	if _, err := TopoOrder(p); err != nil {
		return Plan{}, err
	}
	return p, nil
}

// TopoOrder returns a deterministic topological order (Kahn's algorithm,
// lexicographic tie-break) or an error on duplicate ids, unknown
// dependencies, or cycles.
func TopoOrder(p Plan) ([]string, error) {
	byID := map[string]bool{}
	for _, t := range p.Tasks {
		if t.ID == "" {
			return nil, errors.New("task with empty id")
		}
		if byID[t.ID] {
			return nil, fmt.Errorf("duplicate task id %q", t.ID)
		}
		byID[t.ID] = true
	}
	indeg := map[string]int{}
	dependents := map[string][]string{}
	for _, t := range p.Tasks {
		for _, d := range t.DependsOn {
			if !byID[d] {
				return nil, fmt.Errorf("task %q depends on unknown task %q", t.ID, d)
			}
			indeg[t.ID]++
			dependents[d] = append(dependents[d], t.ID)
		}
	}
	var ready, order []string
	for _, t := range p.Tasks {
		if indeg[t.ID] == 0 {
			ready = append(ready, t.ID)
		}
	}
	sort.Strings(ready)
	for len(ready) > 0 {
		id := ready[0]
		ready = ready[1:]
		order = append(order, id)
		grew := false
		for _, dep := range dependents[id] {
			if indeg[dep]--; indeg[dep] == 0 {
				ready = append(ready, dep)
				grew = true
			}
		}
		if grew {
			sort.Strings(ready)
		}
	}
	if len(order) != len(p.Tasks) {
		return nil, errors.New("dependency cycle detected")
	}
	return order, nil
}

// Orchestrator runs a Plan. Configure the exported fields, then call Run.
type Orchestrator struct {
	Plan        Plan
	PlanPath    string
	Parallel    int
	TaskTimeout time.Duration

	mu     sync.Mutex
	status map[string]*TaskStatus
	byID   map[string]Task
	order  []string
}

// DryRun prints the topological execution order without running anything.
func (o *Orchestrator) DryRun(w io.Writer) error {
	order, err := TopoOrder(o.Plan)
	if err != nil {
		return err
	}
	byID := map[string]Task{}
	for _, t := range o.Plan.Tasks {
		byID[t.ID] = t
	}
	fmt.Fprintf(w, "execution order (%d tasks):\n", len(order))
	for i, id := range order {
		deps := "-"
		if t := byID[id]; len(t.DependsOn) > 0 {
			deps = strings.Join(t.DependsOn, ", ")
		}
		fmt.Fprintf(w, "  %d. %s  [%s]  deps: %s\n", i+1, id, byID[id].Layer, deps)
	}
	return nil
}

// Run executes the plan and returns the summary. It only errors on plan
// or bookkeeping problems; task failures are reported via states.
func (o *Orchestrator) Run(ctx context.Context) (Summary, error) {
	order, err := TopoOrder(o.Plan)
	if err != nil {
		return Summary{}, err
	}
	o.order = order
	if o.Parallel < 1 {
		o.Parallel = 1
	}
	o.byID = map[string]Task{}
	o.status = map[string]*TaskStatus{}
	for _, t := range o.Plan.Tasks {
		o.byID[t.ID] = t
		o.status[t.ID] = &TaskStatus{ID: t.ID, Layer: t.Layer, State: "pending"}
	}
	if err := o.update(func() {}); err != nil {
		return Summary{}, err
	}
	type result struct {
		id string
		ok bool
	}
	results := make(chan result)
	running := 0
	for {
		for running < o.Parallel {
			id, found := o.nextReady()
			if !found {
				break
			}
			o.update(func() {
				s := o.status[id]
				s.State = "running"
				s.StartedAt = now()
			})
			running++
			go func(t Task) { results <- result{t.ID, o.runTask(ctx, t)} }(o.byID[id])
		}
		if running == 0 {
			break
		}
		r := <-results
		running--
		if !r.ok {
			o.update(o.blockDependentsLocked) // cascade: mark blocked children failed
		}
	}
	return o.summary(), nil
}

// nextReady picks the first pending task whose dependencies are all done.
func (o *Orchestrator) nextReady() (string, bool) {
	o.mu.Lock()
	defer o.mu.Unlock()
	for _, id := range o.order {
		if o.status[id].State != "pending" {
			continue
		}
		ready := true
		for _, d := range o.byID[id].DependsOn {
			if o.status[d].State != "done" {
				ready = false
				break
			}
		}
		if ready {
			return id, true
		}
	}
	return "", false
}

// runTask drives one task's dispatch -> verify -> retry loop under a single
// per-task timeout. Returns true iff the task reached "done".
func (o *Orchestrator) runTask(ctx context.Context, t Task) bool {
	if o.TaskTimeout > 0 {
		var cancel context.CancelFunc
		ctx, cancel = context.WithTimeout(ctx, o.TaskTimeout)
		defer cancel()
	}
	prevFailure := ""
	for attempt := 1; attempt <= t.MaxAttempts; attempt++ {
		o.update(func() { o.status[t.ID].Attempts = attempt })
		out, err := runShell(ctx, t.ExecCmd, prevFailure)
		if err == nil {
			vout, verr := runShell(ctx, t.VerifyCmd, "")
			if verr == nil {
				o.finish(t.ID, "done", vout)
				return true
			}
			prevFailure = fmt.Sprintf("verify failed (attempt %d, %v):\n%s", attempt, verr, vout)
		} else {
			prevFailure = fmt.Sprintf("exec failed (attempt %d, %v):\n%s", attempt, err, out)
		}
		o.update(func() { o.status[t.ID].LastVerifyOutput = truncate(prevFailure) })
		if ctx.Err() != nil {
			prevFailure = "task timeout: " + prevFailure
			break
		}
	}
	o.finish(t.ID, "escalate", prevFailure)
	return false
}

// blockDependentsLocked marks (transitively) every pending task that depends
// on a failed or escalated task as failed. Caller holds o.mu via update.
func (o *Orchestrator) blockDependentsLocked() {
	for changed := true; changed; {
		changed = false
		for _, t := range o.Plan.Tasks {
			s := o.status[t.ID]
			if s.State != "pending" {
				continue
			}
			for _, d := range t.DependsOn {
				if ds := o.status[d].State; ds == "failed" || ds == "escalate" {
					s.State = "failed"
					s.LastVerifyOutput = fmt.Sprintf("blocked: dependency %q ended in state %s", d, ds)
					s.FinishedAt = now()
					changed = true
					break
				}
			}
		}
	}
}

func (o *Orchestrator) finish(id, state, output string) {
	o.update(func() {
		s := o.status[id]
		s.State = state
		s.LastVerifyOutput = truncate(output)
		s.FinishedAt = now()
	})
}

// update applies fn under the lock, then atomically rewrites status.json.
func (o *Orchestrator) update(fn func()) error {
	o.mu.Lock()
	defer o.mu.Unlock()
	fn()
	sf := statusFile{Plan: filepath.Base(o.PlanPath), UpdatedAt: now()}
	for _, id := range o.order {
		sf.Tasks = append(sf.Tasks, *o.status[id])
	}
	sort.Slice(sf.Tasks, func(i, j int) bool { return sf.Tasks[i].ID < sf.Tasks[j].ID })
	raw, err := json.MarshalIndent(sf, "", "  ")
	if err != nil {
		return err
	}
	dir := filepath.Dir(o.PlanPath)
	tmp, err := os.CreateTemp(dir, ".status-*.tmp")
	if err != nil {
		return err
	}
	defer os.Remove(tmp.Name()) // no-op after successful rename
	if _, err := tmp.Write(raw); err != nil {
		tmp.Close()
		return err
	}
	if err := tmp.Close(); err != nil {
		return err
	}
	return os.Rename(tmp.Name(), filepath.Join(dir, "status.json"))
}

func (o *Orchestrator) summary() Summary {
	o.mu.Lock()
	defer o.mu.Unlock()
	s := Summary{Total: len(o.status)}
	for _, ts := range o.status {
		switch ts.State {
		case "done":
			s.Done++
		case "failed":
			s.Failed++
		case "escalate":
			s.Escalate++
		}
	}
	return s
}

// runShell runs cmdStr via /bin/sh -c with QL_PREV_FAILURE set, returning
// combined stdout+stderr. On timeout the whole process group is killed so
// grandchildren cannot outlive the task.
func runShell(ctx context.Context, cmdStr, prevFailure string) (string, error) {
	cmd := exec.CommandContext(ctx, "/bin/sh", "-c", cmdStr)
	cmd.Env = append(os.Environ(), prevFailureEnvVar+"="+prevFailure)
	cmd.SysProcAttr = &syscall.SysProcAttr{Setpgid: true}
	cmd.Cancel = func() error { return syscall.Kill(-cmd.Process.Pid, syscall.SIGKILL) }
	cmd.WaitDelay = time.Second // don't block on orphaned pipe holders
	out, err := cmd.CombinedOutput()
	if err == nil && ctx.Err() != nil {
		err = ctx.Err()
	}
	return string(out), err
}

func truncate(s string) string {
	if len(s) > outputTruncateLen {
		return s[:outputTruncateLen]
	}
	return s
}

func now() string { return time.Now().UTC().Format(time.RFC3339) }
