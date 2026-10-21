# Architectural Design Decisions (ADDs) for Monitoring RL/RLHF Systems

This catalogue aggregates all currently identified Architectural Design Decisions (ADDs), their decision options, and decision drivers (forces) for monitoring and responding to issues in reinforcement‑learning‑based and RLHF‑aligned systems.

---

## ADD 1: Safe Exploration Strategy Selection

**Question.** How should deployed RL agents balance exploration of new actions with exploitation of known‑good policies in production, where unsafe exploration can cause harm or violate constraints?

**Key trade‑off.** Adaptation speed vs. safety risk.

### Decision Options

| Option | Brief Description |
| --- | --- |
| Conservative Policy Updates | Limit policy changes per update so new policies do not deviate dramatically from a proven baseline. |
| Constrained Policy Optimisation | Build safety constraints directly into the optimisation objective (e.g. safe RL, constrained MDPs). |
| Multi‑Armed Bandit Integration | Use bandit approaches for low‑risk exploration of policy variants, especially in recommender and ranking systems. |

### Decision Drivers

| Driver | Impact |
| --- | --- |
| SafetyConstraints | Favour constrained and conservative strategies where user or system harm is possible. |
| EnvironmentNonStationarity | Requires some exploration to adapt to changing conditions but within a safe envelope. |
| CatastrophicDegradation | Pushes away from aggressive updates that can suddenly degrade performance. |
| DelayedSparseRewards | Makes pure RL exploration fragile; bandit strategies can be more robust where reward is noisy/delayed. |

---

## ADD 2: Production Monitoring Signal Selection

**Question.** Which signals should be monitored in production to detect performance degradation, unsafe behaviour, alignment drift, or environmental change in deployed RL/RLHF systems?

**Key trade‑off.** Coverage vs. complexity and operational cost.

### Decision Options

| Option | Brief Description |
| --- | --- |
| RL‑Specific Metric Tracking | Monitor episodic return, reward signals, exploration rates, policy entropy, learning progress. |
| Business Outcome Correlation | Track downstream KPIs (conversion, revenue, safety incidents) and correlate them with agent behaviour. |
| A/B Policy Comparison | Continuously compare new policies against baselines via controlled traffic splits. |
| Covariance‑Weighted Reward Signal | Apply statistically efficient tests to reward sequences (e.g. covariance‑weighted means, Hotelling). |
| Feature Distribution Drift (KL/MMD) | Monitor covariate/input distribution shift using KL divergence, MMD, PSI, etc. |
| Reward Proxy Gap Tracking | Compare offline/validation reward estimates with live proxy metrics to reveal eval–deployment gaps. |
| Embedding Drift Detection | Track drift in state/input embeddings or query clusters over time to detect semantic shift. |
| Activation Delta Monitoring | Model‑internal activation deltas as a signal of task drift or concept shift. |
| Reward Model Score Monitoring | For RLHF systems, score sampled production interactions with a (frozen) reward model. |
| KL Divergence from Reference Policy | Track divergence between deployed policy and a known‑good reference (e.g. SFT policy). |
| Metric Divergence Monitoring | Compare an optimised metric against related metrics; divergence suggests specification gaming. |
| Shield Intervention Rate Tracking | Monitor how often safety shields or rule‑based guards override or block proposed actions. |
| Context‑Sliced Signal Monitoring | Compute metrics sliced by context (interaction type, tool usage mode, risk band) rather than only in aggregate. |
| Action Failure Rate Monitoring | Track rates of failed, rolled‑back, or rejected actions as first‑class operational signals. |
| Latency SLO Monitoring | Monitor latency and error SLOs as monitoring signals alongside reward and drift metrics. |
| Security‑Significant Signals | Monitor anomalous tool usage, data‑access patterns, and other security‑relevant behaviours (for agentic RLHF systems). |

### Decision Drivers

| Driver | Impact |
| --- | --- |
| EnvironmentNonStationarity | Favour signals that reveal both internal policy issues and external environment drift. |
| DelayedSparseRewards | Drives use of business KPIs and multi‑metric approaches rather than relying on raw reward alone. |
| CatastrophicDegradation | Increases emphasis on early‑warning signals and A/B comparisons to detect regressions quickly. |
| MonitoringIndependence | Favour external, black‑box signals where modifying the agent is undesirable or impossible. |
| SignalNonStationarity | Motivates statistically robust tests (covariance‑weighted, drift indices) over naive moving averages. |
| GoodhartsLaw | Argues against single‑metric monitoring; supports diverse, cross‑validated signals. |
| CovariateShift | Encourages feature‑distribution and embedding‑drift monitoring to detect static and dynamic shift. |
| EvaluationMismatch | Favour reward proxy gap metrics and multi‑metric evaluation where offline metrics may mislead. |
| RewardModelStaleness | Justifies structural measures like KL to reference policies in addition to reward‑model scores. |
| AlignmentImpermanence | Supports ongoing alignment‑specific signals (reward‑model scores, safety‑flag rates). |
| ScaleCompounding | As agents become more capable, pushes towards multi‑signal monitoring that is harder to game. |
| HiddenVariableShift | Motivates shield‑intervention and embedding‑drift signals beyond state‑space monitoring. |
| DriftInevitability | Underlines need for proactive drift detection (embedding drift, PSI/KL) even when performance seems stable. |
| MonitoringMultiplicity | Encourages combining several complementary metrics and detectors instead of relying on one. |
| SLOBreachDetection | Drives inclusion of latency, error, and failure SLO metrics as first‑class monitoring signals. |
| SecurityCompliance | Motivates monitoring of security‑significant behaviours and tamper‑resistant telemetry flows. |
| GovernanceTraceability | Favors signals whose baselines and thresholds can be versioned, audited, and explained. |

---

## ADD 3: Automated Response Mechanism Selection

**Question.** How should the system respond when monitoring detects problems (degradation, unsafe behaviour, alignment issues) in a deployed RL/RLHF system?

**Key trade‑off.** Response speed and safety vs. operational disruption and cost.

### Decision Options

| Option | Brief Description |
| --- | --- |
| Automated Circuit Breakers | Automatically switch to a safe fallback policy or rules when monitored signals cross critical thresholds. |
| Policy Rollback | Revert to a previously validated baseline policy or checkpoint. |
| Rollback with Learning‑Rate Stabilisation | After rollback, resume training with a reduced learning rate to avoid oscillations. |
| Blue–Green Traffic Shift | Use infrastructure‑level traffic switching (blue/green or canary) to revert quickly without complex state restoration. |
| Graceful Degradation | Reduce the agent’s autonomy/capabilities while maintaining partial service. |
| Human‑in‑the‑Loop Intervention | Require human approval or takeover for high‑risk decisions or when anomalies are detected. |
| Continuous Adaptation (Fine‑tuning) | Trigger fine‑tuning or continuous learning on new data as a response to drift. |
| Mid‑Run Reward Function Update | Adjust reward functions and constraints mid‑run when reward hacking or proxy misalignment is detected. |
| Shadow Deployment | Run candidate policies in “observer” mode to collect data and assess performance without taking real actions. |

### Decision Drivers

| Driver | Impact |
| --- | --- |
| CatastrophicDegradation | Strongly favours fast responses such as circuit breakers and immediate rollback. |
| SafetyConstraints | Increases reliance on HITL intervention and conservative fail‑safes in high‑stakes domains. |
| EnvironmentNonStationarity | Makes graceful degradation and continuous adaptation attractive to maintain service while adapting. |
| EmergentInstability | Supports rollback to known‑good policies when multi‑agent or environment dynamics become unstable. |
| StatefulRollbackComplexity | Encourages infra‑side blue–green switching for stateful agents where full state restoration is complex. |
| FlappingRisk | Discourages overly aggressive triggers that cause frequent rollbacks and redeployments. |
| AuditRequirement | Requires that all automated responses be logged with triggers, timestamps, and versions. |
| RetrainingCost | Trade‑off between continuous adaptation (expensive but flexible) and simple rollback (cheap but static). |
| CatastrophicForgetting | Warns against overly aggressive continuous adaptation that erodes prior capabilities. |
| LatencySLOPressure | Drives automated responses (degradation, rollback) when latency/error SLOs are violated. |
| SecurityCompliance | Motivates kill switches, isolation mechanisms, and security‑team workflows on anomalous or policy‑violating behaviour. |
| GovernanceTraceability | Favours responses whose triggers and policies can be audited and explained post‑hoc. |

---

## ADD 4: Reward Degradation Test Statistic Selection

**Question.** Which statistical test should be used to detect deterioration in reward signals for a deployed RL agent (often with a fixed policy) in episodic settings?

**Key trade‑off.** Detection power and robustness vs. assumptions, complexity, and interpretability.

### Decision Options

| Option | Brief Description |
| --- | --- |
| Covariance‑Weighted Mean Test | Use covariance‑weighted means of episodic rewards for efficient change detection under correlated rewards. |
| Naive Simple Mean | Compare recent mean reward to a baseline; simple but statistically sub‑optimal. |
| CUSUM Sequential Test | Apply classical cumulative‑sum change‑detection to reward sequences. |
| Hotelling Multivariate Test | Use multivariate mean‑shift tests over reward vectors. |
| Embedding‑Based Drift Detection | Detect environmental changes by monitoring state/observation embeddings directly. |
| PSI / KL Input Distribution Test | Use PSI or KL divergence on inputs as a proxy for upcoming reward degradation. |

### Decision Drivers

| Driver | Impact |
| --- | --- |
| DetectionLatency | Favours tests (e.g. covariance‑weighted) that detect degradation quickly. |
| SignalNonStationarity | Pushes towards methods that handle non‑i.i.d., correlated episodic rewards. |
| EpisodicStructure | Enables methods that exploit episodic boundaries (bootstrap, BFAR) but limit applicability to episodic tasks. |
| ReferenceDatasetAvailability | Required for tests that compare against a “valid” reward baseline. |
| MonitoringIndependence | Supports external tests that do not require access to agent internals. |
| GoodhartsLaw | Reminds that reward‑only tests can be gamed; they must be paired with other ADDs (e.g. ADD 6). |
| DriftInevitability | Motivates embedding and input‑distribution tests that can pre‑empt reward degradation. |
| RewardInflationRisk | Highlights that reward hacking can keep or raise rewards while true performance falls. |
| GovernanceTraceability | Favours tests and thresholds whose assumptions and calibration can be documented and audited. |

---

## ADD 5: False Alarm Rate Control Method

**Question.** How should detection thresholds and procedures be chosen to control false alarm rate for sequential online monitoring?

**Key trade‑off.** Avoiding missed detections vs. preventing “flapping” and alert fatigue.

### Decision Options

| Option | Brief Description |
| --- | --- |
| Bootstrap FAR (BFAR) | Use bootstrap methods to control false‑alarm probability over a sequence of episodes. |
| Fixed Statistical Threshold | Apply static thresholds based on assumed distributions (often i.i.d.). |
| Adaptive Threshold | Adjust thresholds online based on observed statistics or context. |
| Variance‑Tuned Threshold | Calibrate thresholds to historical variance to reduce noise‑driven alerts. |

### Decision Drivers

| Driver | Impact |
| --- | --- |
| FalseAlarmCost | Increases the appeal of methods with explicit FAR guarantees (BFAR) or variance‑tuned thresholds. |
| SignalNonStationarity | Reduces the suitability of i.i.d.‑based fixed thresholds; favours BFAR and adaptive schemes. |
| EpisodicStructure | Enables BFAR that relies on episode‑level assumptions. |
| FlappingRisk | Penalises thresholds that are too aggressive and cause frequent, unnecessary rollbacks or interventions. |
| GovernanceTraceability | Encourages thresholding methods whose FAR and calibration are documented and reproducible. |

---

## ADD 6: Reward Hacking Detection Strategy

**Question.** How should systems detect reward hacking (specification gaming, evaluator deception, in‑context reward hacking, covert misalignment) in deployed RL/RLHF agents?

**Key trade‑off.** Detection coverage vs. cost and the risk that the agent learns to evade detection.

### Decision Options

| Option | Brief Description |
| --- | --- |
| Metric Divergence Detection | Compare optimised metrics against related metrics; divergence suggests gaming. |
| Chain‑of‑Thought (CoT) Analysis | Inspect CoT or internal reasoning traces for signs of hacking intent. |
| Adversarial Testing | Deliberately search for reward‑hacking exploits pre‑ or post‑deployment. |
| Ensemble Reward Model Agreement | Use multiple reward models and require agreement to reduce single‑model exploitability. |
| Behavioural Testing on Held‑Out Environments | Test agents in unseen environments to see if hacking generalises. |
| Anomaly Detection with Trusted Policy | Use a trusted baseline policy to flag anomalous action distributions. |
| Deployment‑Time Feedback Loop Simulation | Simulate self‑refinement and feedback loops to detect inference‑time hacking. |
| Reward Model vs Outcome Divergence | Compare reward‑model scores with actual outcomes; divergence may indicate hacking of the reward model. |
| Verbalisation / Self‑Report (VFT) | Train models to explicitly verbalise when they are exploiting shortcuts, improving detectability. |

### Decision Drivers

| Driver | Impact |
| --- | --- |
| GoodhartsLaw | Undermines any single‑metric approach; motivates metric divergence and multi‑signal detection. |
| SpecificationGaming | Encourages adversarial and behavioural testing targeted at known loopholes. |
| ScaleCompounding | More capable agents find subtler hacks, increasing the need for robust and layered detectors. |
| EvaluatorDeception | Reduces reliance on human review alone and motivates CoT analysis and structural checks. |
| CovertMisalignment | Increases value of internal‑reasoning and VFT‑style approaches while acknowledging evasion risk. |
| UnhackabilityHardness | Implies no perfect detector; layered detection strategies are required. |
| AlignmentSideEffects | Encourages metric divergence detection to catch sycophancy, capability suppression, and similar effects. |
| InContextRewardHacking | Motivates monitoring of feedback loops and iterative self‑refinement processes. |
| EvaluatorHackability | Reduces trust in LLM‑as‑evaluator alone; favours ensembles and human oversight. |
| HackingGeneralisation | Suggests testing across many tasks and environments, not just training‑like ones. |
| MonitoringEvasion | Motivates hardened monitoring infrastructure and separation of agent and monitoring code. |
| ContextDependentMisalignment | Encourages scenario‑rich testing beyond simple prompts. |
| VerifierExploitability | Motivates hybrid verification (e.g. VFT plus non‑model‑based checks). |
| RewardModelStaleness | Encourages comparing reward‑model evaluations with real outcomes over time. |
| InContextRewardHacking (deployment‑time) | Supports feedback‑loop simulation and CoT monitoring of refinement steps. |
| CoTFaithfulness | CoTAnalysis is powerful when CoTs are fairly faithful but can be undermined if CoTs are themselves optimised or sanitised. |

---

## ADD 7: Reward Hacking Mitigation Architecture

**Question.** How should systems prevent or reduce reward hacking in deployed RL/RLHF agents, beyond detecting it?

**Key trade‑off.** Strength of mitigation vs. implementation complexity, compute cost, and potential impact on capabilities.

### Decision Options

| Option | Brief Description |
| --- | --- |
| Regularisation to Reference Policy | Penalise divergence from a known‑good reference policy (e.g. KL or chi‑squared regularisation). |
| Reward Function Redesign | Use multi‑objective rewards and constraints to make hacking any single metric less beneficial. |
| Preference as Reward (PAR) | Use latent preference representations as reward rather than raw scores to improve robustness. |
| Inoculation Prompting | Train models with prompts that explicitly frame hacking as undesirable to reduce covert misalignment. |
| Targeted RLHF | Focus RLHF data on high‑risk, “agentic” evaluations where hacking is more likely. |
| Periodic Reward‑Model Refresh | Retrain reward models on new preference data to counter staleness. |
| SFT on Non‑Gaming Data | Supervised fine‑tuning on data where hacking is easy to detect and labelled against. |
| Gated Reward Accumulation (G‑RA) | Gate immediate rewards on long‑term outcomes to reduce multi‑step hacking incentives. |
| Myopic Optimisation (MONA‑like) | Limit optimisation horizon to discourage multi‑step reward‑tampering strategies and unlearn existing hacks. |
| Decoupled Approval / Feedback | Collect feedback from queries sampled independently of taken actions to reduce feedback corruption. |

### Decision Drivers

| Driver | Impact |
| --- | --- |
| UnhackabilityHardness | Demands layered mitigations; no single technique suffices. |
| ScaleCompounding | Encourages techniques that remain robust as capabilities scale (PAR, targeted RLHF). |
| CovertMisalignment | Favors inoculation prompting and targeted RLHF to address hidden intent. |
| GoodhartsLaw | Supports multi‑objective rewards and constraints that are harder to game simultaneously. |
| EvaluatorDeception | Motivates regularisation to reference and decoupled approval to reduce evaluator exploitation. |
| RewardModelStaleness | Encourages periodic reward‑model refresh and related maintenance. |
| AlignmentImpermanence | Motivates ongoing targeted RLHF and reward‑model refreshes rather than one‑off alignment. |
| EvaluatorHackability | Favors decoupled approval mechanisms and non‑model‑based feedback where possible. |
| ContextDependentMisalignment | Supports inoculation prompting and scenario‑rich RLHF datasets. |