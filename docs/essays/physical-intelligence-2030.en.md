# The Embodiment Awakening

### A roadmap for the robotics decade — from bits to atoms, 2025–2030

*Part I of a series. Section One is the technology; Section Two maps each technical thesis to tradable exposure, ending in tickers. Part II covers new verbs and robots-building-robots; Part III is the case against this article's own timing.*

> Over the past decade we taught machines to think. Over the next five years we will let them act. This is a judgment call on how that happens — the architecture, the data bet, the hardware, and the money.

---

## The thesis in one page

Robots are at their **GPT-2 moment**. In 2024–2025 we saw the first manipulation policies that *generalize* — one network that folds unseen laundry, clears an arbitrary table, and turns "put the red cup in the sink" into motion. The prize is larger than language's, because language rearranges **bits** and robots rearrange **atoms**, and most of world GDP is transacted in atoms.

My central claim about *how* we get there — the spine of this whole piece — is a bet about **where the data comes from**:

> **The data curriculum is the strategy.** Pre-train the robot's brain on **ego-centric first-person human video** — millions of hours of people doing things with their own hands. Use **teleoperation and UMI-style handheld collection** as the middle ground that adds action labels. And converge, in the limit, on an **Action Video World Model learned directly from ego-centric data** — a model that predicts *what a pair of hands should do next and what will happen* — with the physical robot as a thin actuator underneath it.

Everything else is in service of that bet, and there are four supporting bets that make it work:

1. **How to mine YouTube** — turn the internet's passive video into affordances and latent actions the robot can use.
2. **A high-level VLM planner driving a low-level cerebellum** — a slow reasoning brain that issues subgoals to a fast, local motor policy (the RT-X wiring).
3. **Sim-to-real RL as the *unified* trainer for the cerebellum** — the same recipe that already gives Unitree and its peers superhuman balance, parkour, and fighting, extended from legs to hands.
4. **The physical layer** — rare-earth motors, reducers, and drive control — and the endgame of **robots building robots**.

The road is gated by four locks — **architecture, data, hands, and the physical supply chain.** Section One walks them. Section Two prices them.

---

# SECTION ONE — THE TECHNOLOGY

## 1. Architecture: two brains, split by time

The most important structural fact about a working robot is that it is **not one model but two**, divided by timescale, mirroring cortex and cerebellum:

- **The planner (System 2).** A large vision-language-action or **video-action** model at ~1–10 Hz. It watches, reasons, and emits *subgoals* — a language step, a target keyframe, an affordance, a latent action code. It answers **"what to do next, and what will happen if I do."**
- **The cerebellum (System 1).** A small, low-latency motor policy at ~100–1000 Hz on the body, consuming the subgoal plus proprioception and touch, closing the loop on torque. It answers **"how to move, right now, given contact."**

This is where the field has converged: Google's RT-1 → RT-2 (a VLM emitting action tokens) → **RT-X** (one policy trained on pooled cross-embodiment data) → the Gemini-Robotics split of a reasoning backbone from a fast action decoder; Physical Intelligence's π-series; Figure's Helix. **The wiring diagram is settled.** The open questions are the *interface* between the brains and the *data* behind each — which is the entire game.

Why the split is a law of the problem, not a design choice:

1. **Latency.** Contact goes unstable on the 10 ms scale; a 300 ms hop to a big model cannot catch a slipping egg. Reflex must be small and local.
2. **Data provenance.** The two brains scale on **different data, from different sources, at different costs** (§3–4). This is the crux.
3. **Amortization.** A strong planner *factorizes* a long task into short primitives — which is exactly what lets a small cerebellum succeed, and, per the reliability math, is the difference between a demo and a product.

Hold this two-brain picture. The rest of Section One is about **what feeds each brain, and how.**

## 2. The data curriculum — the core bet, in order

Language models got a gift: the internet *is* their training set. Robots got none — **there is no first-person robot-manipulation corpus on the web.** Torques, contact forces, and end-effector trajectories must be gathered frame by frame. This is the **data wall**, higher and earlier than language's, and it is *the* bottleneck. My bet is that you climb it in a specific order.

### 2.1 Pre-train: ego-centric first-person human video

Humans are already the largest fleet of manipulation-data collectors on Earth; they simply haven't been recording. Smart glasses change that. **Ego-centric video — first-person, hand-centric, near-infinite (Aria, Ray-Ban Meta, and their successors)** — is the only source that matches the robot's own sensor geometry: a head-mounted view of two hands acting on the world.

The reason to pre-train here rather than on third-person video is *isomorphism*. A robot's egocentric camera and a human's head camera induce the **same visual distribution** — the "first-person eagle view." The affordances (where a mug is grasped), the object permanence, the hand-object contact events, the *subgoal grammar* of everyday tasks — all transfer. What does **not** come for free is the action label: you see the hand move, not the torque. That is fine, because the pre-train's job is to build the **planner**, not the cerebellum (see the scaling math in §4).

### 2.2 Middle ground: teleoperation and UMI

Ego-centric video lacks action labels; teleop and UMI supply them.

- **Teleoperation** is the gold standard — perfectly action-labeled, matched to the embodiment — and the least scalable: one operator, one robot, one hour per hour, at \$20–40/hr. It trades labor *linearly* for data, the opposite of scaling. It survives as the **calibration layer**, not the workhorse.
- **UMI-style handheld collection** decouples data from the expensive robot: a ~\$300 gripper-plus-camera rig lets a human do the task by hand, 5–10× faster, *anywhere*. It is the ImageNet move — scale by crowdsourcing human labor rather than buying robots. It is also the natural bridge from §2.1, because a UMI rig *is* an instrumented pair of hands: the same first-person frame, now with a measured gripper action.

Middle-ground data does two jobs: it **grounds** the planner's affordances into real action, and it **fine-tunes** the cerebellum on the specific embodiment.

### 2.3 The target: an Action Video World Model from ego-centric data

The endgame is to collapse the pyramid. Instead of a planner (from video) bolted to a controller (from teleop), learn a single **Action Video World Model** directly from ego-centric data: a generative model that, conditioned on the current first-person view and a goal, *predicts the video of the hands completing the task* — and, because it was trained with UMI/teleop action labels woven in, predicts the **actions** alongside the pixels.

This is the convergence I bet on: **video generation and robot world models become the same object.** A model that can roll out "what my hands will look like doing this, and what the world will do in response" is simultaneously (i) a planner, (ii) a simulator for rehearsal, and (iii) an evaluator. It is the differentiable, learned physics engine, and it has no sim2real gap *by construction*, because it was learned from real first-person experience. Whoever ports the **scale** of video generation onto **action-conditioned** ego-centric video owns the physical world's GPT-4 moment.

### 2.4 Supporting bet: how to mine YouTube

Beneath ego-centric video sits the cheapest layer — the open internet's billions of hours. It is third-person, unlabeled, and messy, but it encodes vast physical common sense (water flows, ropes tangle, tools afford). Three techniques turn it into signal, in rising order of usefulness:

1. **Hand-pose & contact recovery** — reconstruct 3D hand pose and grasp from ordinary video, *mining out* pseudo-action labels.
2. **Latent actions** — don't recover explicit action; learn a self-supervised "what changed between frames" code, and pre-train the planner to predict it. This is the highest-leverage idea, because it needs no labels at all and scales to the whole corpus.
3. **Affordance & world-model pretraining** — learn where things can be acted on and what follows, feeding §2.3.

YouTube is the base of the pyramid: it can't teach contact control, but it makes the planner *cheap and broad* — which, per §4, is what deflates the price of the expensive action data.

### 2.5 Supporting bet: the VLM planner → cerebellum interface

The planner is a VLM (or video model) that thinks; the cerebellum is a reflex that acts. **The whole system lives or dies on the interface between them.** The candidate currencies, roughly from coarse to dense:

- **language subgoals** ("open the top drawer") — interpretable, but low-bandwidth and ambiguous at contact;
- **keyframes / goal images** — the planner *draws* the next desired state; the cerebellum servos toward it;
- **affordances / trajectories** — 2D/3D grasp points and paths;
- **latent goal codes** — a learned vector the cerebellum was co-trained to consume — highest bandwidth, least interpretable.

My read: production systems will use a **hybrid** — language for task structure, keyframes/latents for the contact-rich last centimeter — and the interface will standardize much the way "tokens" standardized NLP. The planner also owns *failure detection*: when the cerebellum stalls, the planner re-issues a subgoal. That closed loop is not a nicety; §4.3 shows it changes the reliability exponent.

### 2.6 Supporting bet: sim-to-real RL as the unified cerebellum trainer

Where does the cerebellum's *skill* come from, beyond imitation? From **sim-to-real reinforcement learning** — and here the most important existence proof is already shipping in **legged locomotion**. Unitree, Boston Dynamics, and the broader quadruped/humanoid field train whole-body controllers in **massively parallel simulation** (tens of thousands of parallel environments), with domain randomization over mass, friction, latency, and terrain, then transfer zero-shot to hardware. The result is the superhuman balance recovery, parkour, dancing, and sparring you've seen. Locomotion sim2real *works*.

The bet is that **the same recipe becomes the unified trainer for the manipulation cerebellum** — one RL-in-sim pipeline that produces both "keep your balance while shoved" and "seat the connector while it binds." The attractions: infinite, cheap, perfectly-labeled interaction; automatic curriculum; and policies that are *reactive* by construction (they were trained to recover). The honest caveat, which I'll sharpen in Part III: **manipulation sim2real is materially harder than locomotion sim2real**, because rigid-body legged dynamics simulate well while contact-rich, deformable, high-friction manipulation does not. The unifying move is therefore *co-dependent* on §2.3 — a learned Action Video World Model is what makes "sim" faithful enough for manipulation RL to transfer. **Locomotion proved the method; the world model is what extends it to hands.**

## 3. Interlude: the data pyramid as a curriculum

Stack the bets and the pyramid stops being a menu and becomes a *training curriculum*:

```
   pre-train      ┌──────────────────────────────────────┐
   (planner)      │ YouTube (latent actions, affordances) │  cheapest, broadest
                  ├──────────────────────────────────────┤
                  │ Ego-centric first-person human video  │  ← THE core bet
   middle ground  ├──────────────────────────────────────┤
   (grounding)    │ UMI handheld  →  Teleoperation        │  adds action labels
                  ├──────────────────────────────────────┤
   skill / target │ Sim-to-real RL  +  Action Video World │  reactive policy +
                  │ Model (learned from ego-centric data) │  faithful simulator
                  └──────────────────────────────────────┘
```

Read top to bottom, it is exactly the human developmental order: watch, then be guided, then practice. That is the shape of my bet.

## 4. A scaling law for physical intelligence

Language scaling is a near-religion because loss falls as a smooth power law you can *buy*. The right question for robots is **"scaling in what, and does the currency to buy it exist?"**

### 4.1 The two-curve law

Bound the system's failure rate by the *worse* of its two brains, each on its own data:

```
   E_system ≈ max( E_planner(H_v) , E_cerebellum(H_a) )
   E(H) ≈ E∞ + c · H^(−α),      α ≈ 0.1–0.4
```

where `H_v` = hours of **passive video** (YouTube + ego-centric) and `H_a` = hours of **action-labeled interaction** (teleop + UMI + sim). Plug in today's scales:

| Brain | Data currency | Available now | Cost of 10× | Position on curve |
|---|---|---|---|---|
| Planner | video hours `H_v` | 10^5–10^7 h | low, falling | **far along** — near `E∞` |
| Cerebellum | action hours `H_a` | 10^3–10^5 h | high | **early** — steep part |

**This table is the strategy in miniature.** The planner's fuel is cheap and abundant; ego-centric + YouTube pretraining pushes it near its floor. The cerebellum's fuel is scarce and dear, so `E_cerebellum` dominates. The marginal dollar of capability buys **action data**, and the field's true bottleneck is `H_a`.

### 4.2 What actually scales with video hours

You asked the precise question: *what scales with the hours of video?* The answer is **the planner, not the cerebellum** — and that is worth more than it sounds, via a second-order effect.

Video hours buy the planner (i) an **affordance prior**, (ii) a **predictive world model**, and (iii) a **subgoal vocabulary** — none needing action labels. So a *video-action planner trained on ego-centric video, prompting a small RT-X cerebellum, is the right bet*: labeled data is spent only on what video cannot teach, closed-loop contact.

The second-order effect is **amortization**. Let `H_a(target)` be the action data needed to hit a target reliability:

```
   H_a(target) ≈ k · P^(−β) · (task horizon),     P = planner quality
```

Video hours raise `P`, which *lowers the action hours you must buy.* The planner doesn't replace the cerebellum's data — it **deflates its price.** The winner maximizes `H_v × H_a` and uses `H_v` (via the world model, §2.3) to bend down the cost and improve the fidelity of `H_a`. That is the entire reason to care about video, made quantitative.

### 4.3 The reliability wall — why demos ≠ products

The arithmetic that kills naïve optimism. A useful chore is a long horizon of contact-rich steps; open-loop, a `T`-step task at per-step success `p` succeeds with `p^T`:

```
   T = 20, p = 0.95  →  0.95^20 ≈ 0.36        (fails ~2 of 3 attempts)
   0.99 end-to-end at T = 20  →  p ≈ 0.99^(1/20) ≈ 0.99950
```

Demo-to-product is a **100× cut in per-step failure** — the manipulation twin of self-driving's last 1%, and where timelines die (Part III). The escape is the closed loop: give the cerebellum `k` reactive attempts per step (detect slip, re-grasp):

```
   p_eff = 1 − (1 − p)^k
   p = 0.95, k = 3  →  p_eff ≈ 0.99988   →   p_eff^20 ≈ 0.9975
```

**Reactivity changes the exponent, not just the constant.** The planner→cerebellum split earns its keep here: the planner notices failure and re-prompts, turning a brittle `p^T` into a robust product. Reliability is *architectural*, not merely data-driven.

### 4.4 Emergence and the embodiment axis

- **A new axis: embodiments `N`.** Deployed robots collect data while they work (shadow-mode). Capability scales in fielded units — an axis LLMs lack — binding scaling to *deployment*: you must sell robots to scale intelligence. First mover into the flywheel compounds. **This, not architecture or hardware, is the moat.**
- **An emergence threshold.** Expect a phase transition to cross-task generalization once **task-diversity coverage** crosses a threshold — my guess, ~10^7–10^8 quality trajectories for a leading operator, ~2027–2029. Diversity beats depth (10^4 tasks × 10^2 demos ≫ 10^2 × 10^4). This is UMI's deep rationale: it buys breadth cheaply.

## 5. Hardware — the physical layer

Software plans; atoms resist. Five hardware truths decide who ships.

### 5.1 Motors and the rare-earth lock

High-performance robots use **permanent-magnet synchronous motors** built on **neodymium-iron-boron (NdFeB)**, with dysprosium/terbium for heat tolerance. A humanoid carries 40+ motors and ~2–4 kg of magnet material — hundreds of grams of rare earth. **Scaling humanoids is, materially, a bet on magnets.** The bottleneck isn't reserves (rare earths aren't rare) but **processing and magnet-making**, where China holds ~85–90% of refining and >90% of high-performance NdFeB — near-monopoly in heavy rare earths. It is already a bargaining chip and will be weaponized. Substitutes (ferrite, iron-nitride) lose on power density exactly where humanoids are most sensitive, so **the lock can't be engineered away in five years — only diversified around.**

### 5.2 The reducer — the other bottleneck nobody names

A motor spins fast and weak; joints need slow and strong. Between them sits the **reducer**, and it is as much a bottleneck as the magnet:

- **Harmonic (strain-wave) drives** — near-zero backlash, high ratio, compact; the standard for precise arm joints; hard to manufacture (Harmonic Drive Systems and a few others dominate).
- **Cycloidal / RV drives** — high stiffness and shock tolerance for heavy joints (Nabtesco's domain).
- **Planetary gears** — cheap, backdrivable, moderate precision; common in legs and QDD actuators.

Precision reducers are a **quiet oligopoly** with Japanese incumbents, and they are a real supply constraint on humanoid volume. Cost-down here is as decisive as motor cost-down.

### 5.3 Actuation architecture — direct vs quasi-direct vs tendon

How you connect motor to joint is a defining design choice:

- **Direct drive (DD).** Motor on the joint, no reduction. Perfectly backdrivable and "transparent" (the joint feels forces cleanly), high control bandwidth — but low torque density, heavy, power-hungry. Rare in full humanoids.
- **Quasi-direct drive (QDD).** A large-diameter motor + *low* (≈6–10:1) planetary reduction. The MIT Cheetah lineage. It keeps most of DD's backdrivability and transparency while multiplying torque — ideal for **dynamic, contact-rich, impact-absorbing** joints (legs, and increasingly arms). This is the sweet spot for a reactive cerebellum, because a backdrivable joint makes force control and shock survival natural. My bet: **QDD is the default for the athletic humanoid.**
- **Tendon / cable drive.** Motors in the forearm/torso pull "tendons" to move distal joints. Puts mass proximally, enabling **light, fast, anthropomorphic fingers** — the leading route to true dexterity. Costs: cable stretch, friction, wear, and harder control (nonlinear, hysteretic). This is why **hands** trend tendon-driven while **limbs** trend QDD.
- **Hydraulics.** Unmatched peak power density (old Atlas), but leaks, weight, and efficiency have pushed the field to **electric** for anything meant to be cheap, clean, and mass-produced. Electric won.

Read the body as a hybrid: **QDD proximal joints for power and reactivity, tendon-driven distal hands for dexterity, all electric.**

### 5.4 Motor drive control — the unglamorous moat

Between the policy's torque command and the magnet is a control stack that decides whether the robot is smooth and safe or twitchy and dangerous:

- **Field-oriented control (FOC)** turns a 3-phase motor into a clean torque source; done well, the joint is a programmable spring.
- **Torque/current control with high-bandwidth current loops** (tens of kHz) is what makes backdrivable, compliant, force-sensitive joints — the physical substrate of the reactive cerebellum in §2.6.
- **Sensing & thermal limits.** Absolute encoders, current sensing, and thermal models bound *continuous* torque (motors overheat long before they stall). Much of "how strong is this robot, sustainably" is a thermal-control question, not a peak-torque spec.
- **The chips.** Gate drivers, high-side current sensors, and magnetic position encoders (from the analog/power-semi vendors) are a real, investable layer — motor control is silicon as much as software.

The point: **"how to drive the motor" is a genuine moat.** Backdrivable, thermally-honest, high-bandwidth torque control is hard-won know-how, and it is exactly what a sim-to-real cerebellum needs underneath it.

### 5.5 Robots building robots

The endgame is recursion: robots on the line that **assemble** robots (and cars, and dogs) — Tesla's Optimus-builds-Optimus vision. This is real and near (2027–2029), but measure it by **closure** — the fraction of itself a system can build. Assembling from externally-made motors, reducers, batteries, and chips is ~30–50% closure: valuable for cost-down, but not self-replication. Building the *precision mother-machines* (reducers, bearings, and above all **lithography**) is the last 10%, and the **chip lock** — a humanoid brain needs advanced silicon, which needs an EUV scanner, the apex of human industry — keeps full closure decades away. That is a *feature*: it makes physical takeoff **soft, not hard**, leaving humans a control point at the fab. (Part II treats verbs and recursion in depth.)

## 6. Technical bottom line

1. **Two brains, two data curves.** A slow VLM/video planner prompts a fast RT-X cerebellum. They scale on different fuels.
2. **The data curriculum is the strategy.** Ego-centric first-person video to pre-train the planner; UMI/teleop to ground it; sim2real RL + an Action Video World Model to forge a reactive cerebellum. **That is the bet.**
3. **Video deflates the price of action data.** What scales with video hours is the planner — and a better planner lowers the scarce action hours you must buy.
4. **Reliability is architectural.** `p^T` kills open-loop; the closed loop changes the exponent.
5. **Sim2real RL is the unified skill engine** — proven in locomotion, extended to hands by the world model.
6. **Hardware decides who ships:** magnets, reducers, QDD-vs-tendon, and drive-control know-how — half of this is NdFeB and gearboxes.
7. **Robots building robots is soft takeoff**, gated at the fab.

---

# SECTION TWO — THE INVESTMENT MAP

*Not investment advice. Every name below is a tradable proxy for a technical thesis in Section One; sizing, valuation, and timing are yours. Many of the best pure-plays (Figure, Physical Intelligence, Skild, 1X, and Unitree in part) are **private** — I flag where the public market simply has no clean exposure, because that absence is itself a signal.*

The rule I use: **map each technical thesis to the layer that captures its economics, and prefer picks-and-shovels where the end-market winner is unknowable.** We don't yet know which humanoid brand wins; we do know they all need magnets, reducers, motor-control silicon, and compute.

## 7. Thesis → exposure, layer by layer

### 7.1 The planner & training compute (§1, §2, §4)
The planner is a large multimodal model; training it and the world model is a compute story, and inference migrates to the edge.
- **NVIDIA (NVDA)** — training + the Isaac/Omniverse simulation stack; the double exposure (compute *and* sim).
- **TSMC (TSM)**, **ASML (ASML)** — the fab and the lithography under every brain; also the literal chip lock of §5.5.
- **Ambarella (AMBA)** — edge inference SoCs for cameras/robots; a smaller, higher-beta on-body-compute proxy.
- **Qualcomm (QCOM)**, **Arm (ARM)**, **Broadcom (AVGO)** — on-device inference IP and custom-silicon enablement.
- *Risk:* compute demand is real but crowded and priced; this is the consensus leg.

### 7.2 The data layer — ego-centric & tactile (§2.1, §5-touch)
The core bet is a *data* bet, and the cleanest public proxy is **who ships the glasses and the image sensors.**
- **Meta (META)** — Aria/Ray-Ban glasses are the ego-centric data funnel; strategically, glasses are a Trojan horse for physical-world data.
- **Sony (SONY / 6758.T)** — dominant CMOS image sensors; the eyes of both glasses and robots.
- **TE Connectivity (TEL)**, **Amphenol (APH)** — sensors, connectors, and the wiring harness of every robot.
- *No clean public tactile pure-play exists* — vision-based tactile is startup/private. The absence is the tell: touch is early. Watch for IPOs.

### 7.3 Motors & motion control (§5.1, §5.4)
The cerebellum needs backdrivable, thermally-honest torque — motors plus the silicon that drives them.
- **Nidec (NJDCY / 6594.T)** — the world's motor volume leader; direct humanoid-actuator ambition.
- **Regal Rexnord (RRX)**, **Allient (ALNT)**, **Ametek (AME)**, **Parker Hannifin (PH)**, **Moog (MOG.A)** — motors, drives, and precision motion.
- **Motor-control silicon:** **Allegro MicroSystems (ALGM)** and **Melexis (MELE.BR)** (magnetic position sensing), **Infineon (IFNNY / IFX.DE)**, **STMicro (STM)**, **Texas Instruments (TXN)** (gate drivers, current sensing, FOC MCUs). This is the §5.4 moat, in silicon.
- *Risk:* diversified industrials — robotics is a call option on top of an existing business, so exposure is diluted (which also caps downside).

### 7.4 Reducers & precision mechanics (§5.2)
The quiet oligopoly and a genuine volume constraint on humanoids.
- **Harmonic Drive Systems (6324.T)** — strain-wave reducers; arguably the *purest* humanoid pick-and-shovel that trades publicly.
- **Nabtesco (6268.T)** — cycloidal/RV reducers for heavy, high-stiffness joints.
- *Risk:* Japan-listed, cyclical, and sentiment already runs hot on the humanoid narrative here.

### 7.5 Rare earths & magnets (§5.1)
The physical lock, and the most geopolitically reflexive leg.
- **MP Materials (MP)** — the flagship U.S. rare-earth mine + magnet build-out; the Western de-risking trade.
- **Lynas (LYSCF / LYC.AX)** — the largest ex-China separator.
- **Energy Fuels (UUUU)**, **Neo Performance Materials (NEO.TO)**, **USA Rare Earth (USAR)** — processing/magnet plays further up the risk curve.
- **Shin-Etsu Chemical (SHECY / 4063.T)**, **TDK (6762.T)** — incumbent high-performance magnet makers.
- *Risk:* prices are policy-driven and violently reflexive; theses can be right on demand and still whipsawed on subsidy/tariff headlines.

### 7.6 Batteries & power (§5)
A humanoid is "an EV that grew hands"; it shares the EV cell and power chain.
- **CATL (300750.SZ)**, **Panasonic (PCRFY / 6752.T)**, **Samsung SDI (006400.KS)**, **LG Energy (373220.KS)** — cells.
- **Monolithic Power (MPWR)** — power management for compute and actuation.

### 7.7 Sim, world models & software (§2.3, §2.6)
The Action Video World Model and sim2real RL are software; public pure-plays are thin.
- **NVIDIA (NVDA)** again — Isaac Gym / Omniverse is the default sim2real substrate (it appears twice on purpose).
- **Unity (U)** — simulation/rendering exposure, execution-dependent.
- **Synopsys (SNPS)** — post-Ansys, owns physics simulation IP.
- *Most world-model value accrues to private labs* (Physical Intelligence, Skild, Wayve-style) — again, the absence is the signal.

### 7.8 Integrators, OEMs & humanoids (all of §1–§6)
The end-product bet — highest upside, least knowable winner.
- **Tesla (TSLA)** — the only mega-cap where a humanoid (Optimus) is a core thesis *and* the EV supply chain and data flywheel are in-house.
- **Hyundai (HYMTF / 005380.KS)** — owns Boston Dynamics.
- **Xiaomi (1810.HK)**, **UBTech (9880.HK)** — China humanoid exposure (access/ADR caveats).
- **ABB (ABB)**, **Rockwell (ROK)**, **Fanuc (FANUY / 6954.T)**, **Yaskawa (YASKY / 6506.T)**, **Estun (002747.SZ)**, **Inovance (300124.SZ)** — the industrial-automation base that humanoids extend.
- **Intuitive Surgical (ISRG)** — not a humanoid, but the best public proof that *teleoperated dexterity + a razor-and-blades data moat* compounds; a template, not a pure-play.
- **Symbotic (SYM)**, **Serve Robotics (SERV)** — narrow, deployed embodiments already turning the data flywheel in logistics/delivery.
- *Risk:* single-name humanoid bets are venture-shaped inside public wrappers — high dispersion, long duration, and (Part III) exposed to a mid-cycle funding winter.

## 8. How to read this map

- **The consensus leg is compute (7.1); the differentiated legs are reducers (7.4), motor-control silicon (7.3), and magnets (7.5)** — the boring physical chokepoints that must scale no matter which brand wins.
- **The core bet (ego-centric data) has no clean public pure-play** beyond Meta and Sony; its value is being captured privately. If you believe Section One, that is the single most important sentence in Section Two — the market is *underpricing the data layer because it can't buy it.*
- **Prefer picks-and-shovels while the end-market winner is unknown**, and treat single-name humanoids as convex, small-sized options.
- Everything here is **long-duration and reflexive**; Part III explains why being directionally right can still lose money for years in the middle.

---

*Part II: new verbs and robots-building-robots. Part III: the case against this article's timing — the self-driving trap, the reliability chasm, and the funding winter that could bury correct theses on the way up. Written 2026 — a judgment call, not a prophecy.*
