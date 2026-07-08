package main

import (
	"context"
	"flag"
	"fmt"
	"os"
	"time"
)

func main() {
	planPath := flag.String("plan", "", "path to plan.json (required)")
	parallel := flag.Int("parallel", 4, "max concurrent tasks")
	taskTimeout := flag.Duration("task-timeout", 30*time.Minute, "per-task timeout (all attempts)")
	dryRun := flag.Bool("dry-run", false, "print topological execution order and exit")
	flag.Parse()
	if *planPath == "" {
		fmt.Fprintln(os.Stderr, "usage: orchestrator -plan plan.json [-parallel 4] [-task-timeout 30m] [-dry-run]")
		os.Exit(2)
	}
	plan, err := LoadPlan(*planPath)
	if err != nil {
		fmt.Fprintln(os.Stderr, "orchestrator:", err)
		os.Exit(2)
	}
	o := &Orchestrator{Plan: plan, PlanPath: *planPath, Parallel: *parallel, TaskTimeout: *taskTimeout}
	if *dryRun {
		if err := o.DryRun(os.Stdout); err != nil {
			fmt.Fprintln(os.Stderr, "orchestrator:", err)
			os.Exit(2)
		}
		return
	}
	sum, err := o.Run(context.Background())
	if err != nil {
		fmt.Fprintln(os.Stderr, "orchestrator:", err)
		os.Exit(2)
	}
	fmt.Println(sum.String())
	if sum.Done != sum.Total {
		os.Exit(1) // at least one task escalated or was blocked
	}
}
