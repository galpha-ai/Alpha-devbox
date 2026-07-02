# New Verbs and Self-Replication

### Two longer-horizon phase transitions — Part II of the series

*When does a robot learn a genuinely **new verb** — a task outside its training distribution? And when do robots start **building robots**, up to replicating a supply chain? Part I set the five-year roadmap; this part looks past it, at the two transitions that decide whether physical intelligence stays a tool or becomes open-ended.*

> Part I was about scaling the known. Part II is about two discontinuities: the **generalization** transition (inventing new skills) and the **production** transition (self-replication). They arrive at different times — and, crucially, *not at the same time*, which is where safety lives.

---

## Part A — The new-verb problem

### A.1 Verbs, and the neural interface that calls them

Picture a robot's competence as a **dictionary of verbs** — motor primitives: grasp, push, twist, insert, pour, fold, tear. Nouns are objects; verbs are actions; intelligence is the ability to compose a small set of verbs into unbounded behavior. "Cook dinner" is not a verb — it is dozens of verbs (wash, cut, pour, stir, flip) sequenced to context.

A useful frame for the planner→cerebellum interface of Part I is that the cerebellum **exposes verbs as a callable API**, and the planner calls them — a *neural* Model-Context-Protocol for the body. The planner says "now *twist* this cap"; the cerebellum instantiates the closed-loop control. This clarifies the real question: progress splits into **using the verbs you have better**, and **acquiring verbs you don't.** Those two curves peak at very different times.

### A.2 Three levels, routinely conflated

People lump all of this under "generalization." There are three distinct difficulty tiers, and confusing them is the root of most bad forecasting:

- **Level 1 — noun generalization.** Same verb, unseen object: *grasp* a mug you've never seen. Shallow — a vision/geometry problem. **Largely solved, 2025–2026.** Most "generalizing" demos are here. Impressive, but *not a new verb.*
- **Level 2 — compositional generalization.** Known verbs, novel arrangement: complete an untrained long task by re-sequencing verbs you already have. **Solved gradually, 2026–2028**, via the System-2 planner. This covers a *lot* of seemingly-new tasks and is the near-term commercial engine — but it invents nothing; it re-permutes.
- **Level 3 — new-verb acquisition.** Learn an action primitive *not in the dictionary* — face a screw with no demonstration and no "twist" verb, and discover it. **The real frontier; I put a reliable prototype at 2031–2034.**

**The headline point:** 99% of what the press calls "OOD generalization" is Levels 1–2. The genuine article, Level 3, is unsolved and is the actual threshold to open-ended physical intelligence. Don't let Level-2 dazzle read as Level-3 arrival.

### A.3 Where new verbs come from

Three sources, arriving in sequence:

- **A — Human demonstration transfer (now).** A human does the new action once; the robot learns it from ego-centric video / teleop / UMI (Part I's data curriculum). Not invention but *fast imitation* — yet the dictionary grows. **The main 2025–2028 source of "new" verbs.**
- **B — Compositional emergence (~2028).** With a large dictionary and a strong planner, new verbs appear by **interpolating** old ones — "twist" approximated as "rotate + press + maintain contact." This needs the world model of Part I: a differentiable physics intuition lets the robot *imagine* an unseen action's outcome.
- **C — Autonomous invention (2030+).** No demo, no valid composition — the robot **trial-and-errors a new verb** in reality or in the world model. The physical AlphaZero moment: no human playbook, a novel move. Its bottleneck is not the algorithm but the **cost of trial**: real trials are slow, expensive, and break hardware; simulated trials need a faithful world model. **So the timeline for autonomous invention is set by world-model fidelity** — the same keystone the critique in Part III flags.

### A.4 Timeline

| Capability | Form | Call | Confidence |
|---|---|---|---|
| Noun generalization | same verb, new object | 2025–2026 | high |
| Compositional OOD | old verbs, new sequence | 2026–2028, commercial engine | med-high |
| Few-shot new verb | learn from a few demos | 2027–2029 | medium |
| Compositional new verb | extrapolate from old verbs | 2029–2031 prototype | med-low |
| Autonomous invention | no demo, self-discovered | 2031–2034 prototype | low (direction sure) |

**One line:** through 2030, robots get very good at *composing known verbs into new tasks* (Level 2), which will look like general competence; *inventing* new verbs (Level 3) waits until after 2030 and gates on world-model fidelity. When Level 3 lands, robots gain physical creativity independent of humans — a transition deeper than GPT-4.

---

## Part B — Recursive self-improvement: robots building robots

### B.1 The real form: machines making machines

Digital "recursive self-improvement" means AI editing its own weights. The physical version is what matters here: **a special-purpose robot that builds robots, up to replicating its own supply chain** — von Neumann's self-replicating machine, NASA's lunar autofac, the science-fiction von Neumann probe. Its allure: once the loop closes, capacity goes from **linear to exponential** — robots build robots, the population doubles on a cycle, and you no longer need a human to build each unit. It is the only route to a physical "hard takeoff."

The concept most people skip is **closure** — the fraction of itself a system can build.

### B.2 The closure ladder

Closure is the true ruler. 0% = pure human labor; 90% = builds 90% of its own parts, imports the rest; 100% = full self-replication from raw materials and energy. **The last 5–10% is an order of magnitude harder than the first 90%,** because modern robots ride a deep, globally-divided supply chain whose apex — advanced-node chips — is the summit of human industry.

Climb it, easy to hard:

- **Rung 1 — robots assemble robots (2027–2029, ~30–50% closure).** Humanoids on the line torquing bolts, snapping modules together, assembling other robots, cars, dogs. Not hard — assembly is structured. This is Tesla's Optimus-builds-Optimus. But it is **assembly, not manufacture**: the motors, reducers, cells, and chips are still made by external specialists. Huge for cost-down (Part I's cost curve); *not* self-replication.
- **Rung 2 — replicate a mid-tier supply chain (2030–2035, ~60–75%).** Robots also make the *coarse* parts — structures, housings, harnesses, simple motors, reducer shells. Two hard bones stay outside: **advanced chips**, and **rare-earth magnets** (you can wind a motor, but not smelt the NdFeB — Part I's rare-earth lock, again).
- **Rung 3 — build the precision mother-machines (2035–2045, ~80–90%).** Machine tools, precision bearings, optics, sensors. The hardest mother-machine is the **EUV lithography scanner** — the apex of manufacturing complexity, hundreds of thousands of parts and hundreds of top suppliers. Assembling one from finished parts may be possible post-2035; *manufacturing* its parts is near-impossible to close this century.
- **Rung 4 — a lunar TSMC (2045+, or not this century).** Off-world, autonomous, in-situ-resource self-replication of semiconductor fabrication. **Candidly: science fiction on a 5–10-year view.** The realistic near path is a *high-but-not-full-closure* lunar factory — energy, structure, coarse fabrication (~80%) — while the chips still ship from Earth. Expecting the Moon to self-produce 7 nm silicon is moving humanity's most delicate industrial process to its most hostile environment; it violates the economics.

### B.3 The chip lock, and why takeoff is soft

Across every rung, **advanced-node silicon is the ultimate seal.** A robot's brain needs advanced chips; advanced chips need EUV; EUV is what all of human industry, together, barely builds. The paradox:

> For a robot to fully self-replicate, it must build the lithography that builds its own brain — the one machine our whole industrial civilization was required to produce.

So my core call: **physical recursive self-improvement stalls, for decades, at "high closure but not full."** Robots will build robot *bodies* but not robot *brains*. This is good news — humanity keeps a control point and a safety valve **at the fab.** There is no runaway hard takeoff, because it is gated on lithography, a gate humans hold.

### B.4 Timeline

| Stage | Form | Closure | Call | Confidence |
|---|---|---|---|---|
| Robots assemble robots/cars/dogs | assembly, parts imported | 30–50% | 2027–2029 | med-high |
| Replicate mid-tier chain (Unitree-tier) | + coarse parts | 60–75% | 2030–2035 | medium |
| Build precision mother-machines | + machine tools | 80–90% | 2035–2045 | low |
| Lithography / lunar TSMC | near-full incl. chips | 95–99% | 2045+, likely not this century | very low |

---

## Part C — Where the two transitions meet

Combine the halves:

- **New-verb capability** sets how *smart the hands* are — whether a robot copes with the open world.
- **Recursive self-replication** sets how *fast the fleet breeds* — linear vs exponential capacity.

A true **physical intelligence explosion** needs both at once: an army that handles any novel task *and* multiplies itself. But the decisive judgment is that **the two transitions arrive off-cycle, and that staggering is the safety.**

- Level-2 "compose known verbs" arrives fast (2026–2028) — huge value, but bounded, controllable.
- Rung-1 "assemble robots" arrives fast (2027–2029) — capacity jumps, but low closure, human-dependent.
- The dangerous pair — **autonomous new-verb invention × full-closure self-replication** — needs *both* a mature world model *and* chip-level closure, and neither lands before the late 2030s at the earliest.

Two natural brakes therefore hold: **new-verb invention is gated by world-model fidelity; full self-replication is gated by lithography.** Both buy humanity time, control, and the option to intervene. They are not failures of technology; they are **gifts of safety.**

**The two years to watch, further out than Part I's 2030:**
- *~2031–2034:* the first robot that, with no human demonstration, invents a new verb for a novel physical problem — the moment robots gain physical creativity of their own.
- *~2035+:* the first robot-led production line to cross ~80% closure — the moment capacity begins to slip the leash of human labor.

They are further away and more profound than 2030. One is about the **openness of intelligence**, the other about the **autonomy of production.** When they finally meet, humanity will face, for the first time, an artifact that can both *figure out how to do a thing* and *build more of itself to do it.* We still have time — and that time is exactly what lithography and world-model fidelity are buying us. Spend it well.

*Part III is the case against this whole timeline. Written 2026 — a judgment call, not a prophecy.*
