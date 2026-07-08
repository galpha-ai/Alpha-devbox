# Red Team: What Breaks, What's Late, Who Burns

### The assumptions most likely to fail, the timelines most likely to slip, and the self-driving-shaped hole in the middle of the decade

*Part IV of the series — a standalone companion whose job is to argue against the other three. Where the roadmap says "probably," this document asks "what if not, and who dies while we find out."*

---

## 0. The base rate you should be anchored to

Before any object-level critique, the reference class. **Self-driving, 2016:** the architecture had converged (deep perception + planning), the demos were spectacular, the scaling story was coherent ("fleet miles are the corpus"), and the timelines were unanimous — full autonomy by 2019–2021. What actually happened:

- **Argo AI**, ~\$3.6B in, shut down (2022).
- **Cruise**, ~\$10B+ in, defunded (2024).
- **Uber ATG** sold, **Drive.ai** acqui-hired, the trucking SPACs went to approximately zero.
- Cumulative sector investment **north of \$100B for roughly one scaled Western winner** — Waymo, *sixteen years* from founding to meaningful commercial scale — plus a Chinese cohort that survived on different economics.

The technology *was* real. The direction *was* right. **Nearly everyone who bet on the 2016 timeline was destroyed anyway.**

The uncomfortable structural rhyme: robotics 2026 has converged architecture, spectacular demos, a coherent scaling story ("ego video is the corpus"), unanimous timelines, and **multi-billion-dollar rounds at pre-revenue valuations** (Figure at ~\$39B; Apptronik's \$935M Series A). The roadmap's own forecasts cluster in 2027–2030. The self-driving-adjusted prior says: **add three to seven years to every consumer-facing claim, and assume the capital markets will not wait that long politely.**

The rest of this document works out where the roadmap is most exposed, in descending order of how much of the thesis each failure takes down.

---

## 1. The log-linear law is a pessimistic law (and the roadmap cites it as good news)

The strongest evidence for the ego bet — that each doubling of ego hours yields a *constant* improvement — deserves a hostile reading, because **log-linear scaling is exponentially expensive.**

If a doubling buys a constant gain `δ` (in success-rate points, or log-odds), then closing a capability gap `Δ` requires `Δ/δ` doublings — a data multiplier of

```
   H_required / H_0  =  2^(Δ/δ)
```

Plug in generous numbers. From an ~85% demo-grade operating point to the ~99.9% that *unsupervised* commercial operation demands is a large `Δ` in log-odds terms. At `δ ≈ 2–3` points per doubling near the current operating point — and `δ` always *decays* as you climb — you need not one or two more doublings but **five to ten**: `10^5` hours becoming `10^7–10^8` hours. Collectible? Perhaps — a million devices × a hundred hours each. But then the second curse activates.

**The double curse of the tail.** The failures that separate demo from product are long-tail *contact* events — in-hand slip recovery, deformable jams, tolerance-stack surprises. These events are (a) **rare in natural video** — people film cooking, not the 0.1% of cooking where the jar lid cross-threads — and (b) **invisible in video even when present**, because they are *force* phenomena, which the roadmap itself proves are latent in pixels. So the tail is simultaneously **under-sampled and under-observed**: the effective `δ` for exactly the capability that matters commercially is far below the headline `δ` measured on the distribution's body. This is precisely the shape of self-driving's failure — disengagement rates improved log-linearly on fleet miles until the residual failures stopped being i.i.d., and then data scaling became a comically inefficient instrument against structured rare events.

**What this does to the thesis:** it does not falsify the ego bet — it **re-prices** it. Ego video takes you from 60% to 90% cheaply (real, valuable, sufficient for fenced deployments with human fallback). It does *not* take you from 99% to 99.99%. The roadmap's own planner-overhang prediction is the tell: the overhang is not a transitional curiosity — **it may be the steady state of the decade**, planners that know everything paired with hands that still fumble the tail. If so, the "robot ChatGPT moment ~2029–30 at ~65%" line is the single most likely forecast entry to be wrong, and wrong in the expensive direction.

---

## 2. The factorization may not factor

The mathematical heart of the pyramid is the claim that the transition model factors,

```
   p(s' | s, a)  =  ∫ p(s' | w) · p(w | a, M) dw
```

— *world-given-contact* is embodiment-invariant; *contact-given-action* is morphology-specific and low-dimensional. The critique: **the human hand may not admit a low-dimensional retargeting map.** Human manipulation exploits continuous compliance (soft finger pads deforming around geometry), skin friction fields, and *unconscious sub-perceptual force modulation* at millisecond timescales — none of which live in the wrist-pose + MANO-parameter action space that current unified representations use.

If a meaningful fraction of human competence is smuggled through channels that the retargeting map `φ: A_human → A_robot` cannot express, then ego pretraining transfers the **plan** and silently drops the **skill** — and the measured `α > 0` is real but **tops out early**, exactly the saturation the roadmap lists as its own falsifier. The honest status: **`α`'s asymptotic behavior is unmeasured. Everyone is extrapolating from the cheap part of the curve.** (History rhyme: imitation-learning-from-video results in 2018–2022 repeatedly showed early transfer gains that saturated; the field's memory of this is suspiciously short.)

**Second-order version — entanglement.** At `10^6+` hours, the statistically efficient thing for a large model to do is exploit human-hand-specific visual shortcuts, because they are everywhere in the corpus. Preventing entanglement is a permanent adversarial tax paid in augmentation and architecture — and every point of that tax reduces effective `α`.

---

## 3. Force-grounding may never scale — the middle layer as permanent bottleneck

The roadmap's own refinement — *the middle layer's true job is force-grounding; the KPI is force-labeled hours* — is also its soft underbelly. Kinematic ego data scales because a consumer device (Vision Pro, Aria) emits it **as exhaust**. **No consumer device emits force.** Tactile sensors remain fragile, drifty, expensive, and calibration-hungry; instrumented gloves are lab equipment; and the elegant answer — transparent QDD fleets as free force sensors — only produces *robot-side* force data, which is exactly the scarce, deployment-gated currency the pyramid was designed to economize.

If force-labeled hours grow **linearly** (ops-limited) while kinematic hours grow **exponentially** (device-limited), the pyramid becomes a very tall structure standing on a very thin middle, and the binding constraint of the entire program is a **sensor-hardware problem the ML community keeps assuming someone else will solve.** The tactile "electronic skin" line in the Public-Markets Map is simultaneously the highest-option-value and the least-mature entry — that combination is a warning as much as an opportunity.

---

## 4. The world model as gym: the single point of failure, restated adversarially

The roadmap flags contact fidelity (call it **F2**) as its "single correlated risk" and then builds the flywheel on it anyway. State the adversarial case plainly:

- **The hybrid stack** (splats + physics core + video imagination + force correction) **is a systems-integration bet**, and systems-integration bets in ML have a poor record against bitter-lesson monocultures — *but* the monoculture (pure video scaling) provably cannot ground force. So the field may spend **2026–2029 caught between an architecture that can't scale (hybrid, engineering-heavy) and a scaler that can't ground (video).** That deadlock *is* the 1–2 year slip the roadmap prices at the margin; it could be a **4–5 year slip.**
- **The worse-than-nothing regime.** A world model at **F1.5** — visually convincing, dynamically subtly wrong — used as a gym injects *systematic* physics bias into every cerebellum trained inside it. Amplification gain goes negative; **the flywheel spins backward while every dashboard shows data volume going up.** Self-driving analog: simulation-validated stacks that fell over on real long-tails. The failure is insidious precisely because synthetic-data pipelines report *throughput, not truth.*

---

## 5. Unit economics: the safety-driver trap, transposed

Self-driving's capability story was ruined less by capability than by **the supervision ratio.** A safety driver per vehicle deletes the economics; the entire commercial question compressed into "when does one remote operator supervise N > 10 vehicles."

Robotics imports the same trap with new names. Current humanoid deployments run with **teleop fallback and near-1:1 human supervision** — the \$25/robot-hour headline quietly excludes the supervising human, the deployment engineers, and the intervention infrastructure. The commercial crossing is not "the robot works"; it is **interventions-per-hour falling far enough that one operator covers a fleet.** No public deployment discloses this number today, which — per the base rate — is itself the tell (AV companies also stopped publishing disengagement rates when the numbers stopped flattering). Add: **cycle-time parity** (a robot at 0.5× human takt violates line economics even at 99% reliability); **insurance and liability** pricing for mobile manipulators around humans (unpriced; one serious injury event resets the regulatory clock the way Uber–Tempe did for AVs in 2018); and battery/duty-cycle realities. **The roadmap's forecast contains no supervision-ratio line, and it should — that is the variable the entire commercial timeline actually loads on.**

---

## 6. Hardware: cost floors, not cost curves

The roadmap treats the BOM as a declining curve. The critique: several terms have **floors.**

- **Precision grinding** (flexsplines, roller screws at <3 µm) is capex- and skills-bound; harmonic-reducer capacity historically expands at *single-digit multiples per half-decade*, not the 10–30× a 2028 humanoid ramp implies. The Public-Markets Map's "squeeze confirmation" (lead-time/ASP divergence) is, read differently, **the ramp failing.**
- **The rare-earth term.** The sub-\$20K humanoid is, by the roadmap's own arithmetic (~\$46K → ~\$131K ex-China), a bet on Chinese magnet policy. The **Nov 10, 2026 cliff** has a ~40% branch where magnet prices spike *into* the ramp.
- **The QDD coupling cuts both ways.** The learning-optimal actuator is the magnet-heaviest one, so any magnet shock *specifically taxes the architecture the ML roadmap prefers* — a correlated hardware-software risk the market treats as two separate stories.

**Net:** the realistic 2028 BOM may stall in the **\$30–45K band**, which quietly deletes most home-robot and much service-sector TAM math for the rest of the decade, leaving **industrial cells — the segment that least needs a humanoid form factor.**

---

## 7. The timing table: roadmap vs. self-driving-adjusted

| Capability | Roadmap | Bear-but-fair | SDC-adjusted | Note |
|---|---|---|---|---|
| Ego-pretraining α replicated | 2026 [high] | 2026 | 2026 | Safest claim in the roadmap |
| Planner overhang visible | 2027–28 | 2027 | 2027 | The critique *strengthens* this one |
| World-model gym → production rigid-task cerebella | 2027–28 (~60%) | 2029 | 2030–31 | F2-deadlock scenario |
| Skill-acquisition cost crossover | 2028 (~55%) | 2030 | 2032+ | Gated by §3 + §4 jointly |
| Fenced "robot ChatGPT" (warehouse/factory) | 2029–30 (~65%) | 2030–31 | 2032–33 | And *fenced* is doing enormous work |
| Fine force-critical dexterity | not by 2030 | 2033+ | 2035+ | The self-driving-class problem |
| General home robot, unsupervised | beyond horizon | 2033+ | 2036+ | The "full self-driving" of this cycle |
| Supervision ratio 1:10+ | *absent from roadmap* | 2029 | 2031+ | **The commercially decisive line** |

**The pattern to internalize:** capability *demos* will keep arriving on the roadmap's schedule; *products* will arrive on the right-hand column's schedule; and **the valley between those two schedules is where the capital dies.**

---

## 8. Who burns in the valley

If the right-hand column is even half correct, the **2028–2032 middle of the decade is a funding winter** for everyone whose runway assumed the left column. The mortality map, by structural position:

- **Pre-revenue integrators without captive deployment scenes** — the Cruise analog. A ~\$39B valuation requires believing the left column; the burn rate is set today, the revenue arrives on the right. Survivors attach to patient balance sheets (a carmaker's factory, a hyperscaler's treasury, a sovereign program) — the Waymo pattern. Expect the Western humanoid field of ~10 credible integrators to resolve to **2–3, with at least one \$1B+ shutdown that resets sector sentiment for 18 months.**
- **The Chinese integrator cohort** resolves differently but not more gently: dozens of companies + provincial subsidy → a price war that transfers all margin to customers and component makers — the solar/lidar/EV script, where *the technology wins and the equity loses.* Direction right, returns negative.
- **Data-ops companies** ("Scale AI of atoms") get verticalized: once ego capture is device-exhaust (Meta/Apple) and labs run their own UMI fleets, third-party data ops compresses to a services margin. The window is real but **closes by ~2029.**
- **Teleop-heavy service models** are the safety-driver companies of this cycle: revenue that looks like robotics, costs that look like staffing.
- **Component names in the drawdown:** the 2021-SPAC/EV-supplier rhyme — reducer, screw, and magnet equities can trade at ramp-implied multiples in 2026–27, then absorb a **50–70% de-rate in 2028–29** when Optimus lands at the low end of guidance, *even though the 2035 end-state demand is fully intact.* Being early is indistinguishable from being wrong at the position level; the Map's own "50–150K landing = master switch" monitor is, adversarially read, a confession that a 3× range in the key input is unresolved.

**Who survives regardless:** component makers with existing non-robot revenue (reducers into industrial robots, magnets into EVs, machine tools into everything) — they collect the option without paying the burn; hyperscalers, for whom this is a rounding-error R&D line with corpus ownership attached; and the patient-capital labs. Notably, **this surviving set is approximately the barbell the Public-Markets Map already recommends** — so the critique's amendment is not to the barbell's *composition* but to its **timing discipline:** stagger entries on the dashboard's catalysts rather than pre-positioning for the left column, hold the pre-revenue end at option-sized weights, and treat **2028–29 as the accumulation window the drawdown will create, not the harvest the roadmap promises.**

---

## 9. Steel-manning back: why this cycle could beat the base rate

A red team that only attacks is a mood, not an analysis. Three honest disanalogies to self-driving:

1. **Fallback is cheap.** An AV failure at 70 mph is a fatality; a manipulation failure is usually a dropped object. Robotics can ship at 95% with human fallback and **earn revenue while climbing the reliability curve** — AVs structurally could not. This is the strongest single reason timelines here compress relative to the AV-adjusted column, and it applies precisely to the fenced deployments the roadmap forecasts first.
2. **Reward density.** Physical tasks verify locally and immediately (the cup is lifted or it is not); driving verifies globally and rarely (crashes are 10⁻⁶ events). RL compounds where verification is dense — the roadmap's own law — and manipulation sits on the favorable side of that law even though driving did not.
3. **The environment is negotiable.** AVs had to accept the world as given; factories can be re-fenced, re-lit, re-fixtured around the robot. **Every dollar of environment engineering substitutes for a nine of policy reliability** — a degree of freedom self-driving never had.

Weighing both directions: **the fenced-industrial claims survive the critique largely intact (perhaps +1–2 years); the open-world, home, and fine-dexterity claims take the full AV adjustment (+4–7 years);** and the *financial* history rhymes regardless of the technical one, because valuations are set by the left column while cash flows arrive on the right.

---

## 10. What would falsify this critique

Symmetry demands it. This document is wrong — and the roadmap's original timelines stand — if, **by end-2027:**

- **(a)** a supervision ratio ≥ 1:5 is *publicly disclosed and audited* at a commercial humanoid deployment;
- **(b)** the F2 zero-shot number crosses ~80% on genuinely held-out rigid-contact tasks;
- **(c)** measured `α` holds constant through two further orders of magnitude of ego hours (no saturation through `10^7`); or
- **(d)** a consumer device ships with per-interaction force sensing, collapsing §3.

**Two of these four and the left column re-prices; all four and this document should be deleted.**

---

*The purpose of the roadmap is to be right about the destination. The purpose of this document is to keep the portfolio alive long enough to get there. In this asset class those are different skills — and self-driving is the proof.*
