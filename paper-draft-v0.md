# Numbers or Decisions?
## Output Contracts for LLM Customer Agents in Counterfactual Policy Comparison

| Field | Value |
|---|---|
| Status | **FROZEN 2026-11-08** — 기준선, 이후 수정은 v1 |
| Target | Workshop paper, 6-8 pages |
| Candidate venues | EMNLP Industry, KDD workshop, ICWS |
| Data | Synthetic only; no client data |
| Companion | experiment-design-v1 (protocol) |

> **동결.** 이 초안은 2026-11-08 기준선으로 동결한다. 오라클 스윕 24시드에서
> 교차 가설이 지지되지 않았으므로 §1.3 기여 3과 §3.6의 이질성 가설은 v1에서
> 재구성 대상이다. 동결본은 제안 패키지에 첨부하지 않는다.

<!-- anchors: We do not claim the components | ranking fidelity against the analytic ranking | cost-to-stability | 0 wrong conclusions | 10% calibrated logit | no paper | not a reproduction of their numbers -->

---

## Abstract

LLM-simulated customer populations are increasingly used to compare pricing policies that were never deployed. The literature offers two incompatible reporting conventions: elicit a purchase probability from the model, or read a discrete accept/reject decision from it. Both are used to rank policies, yet the two have never been compared under a common population with a known ground truth.

We construct an analytic demand model whose policy ranking is exact, overlay an LLM customer layer on it, and compare three output contracts — numeric probability, binary decision, and binary decision with a reason code — under an equal compute budget. We report **ranking fidelity against the analytic ranking**, direction accuracy over policy pairs, and the number of calls required for the ranking to stabilize.

[MAIN RESULT — TBD]

We do not claim the components. Calibration, trace-based diagnostics, abstention, and preregistration are established in prior work; we adopt them. The contribution is the comparison itself, conducted against a reference ranking rather than against predictive fit.

---

## 1. Introduction

### 1.1 Problem

Counterfactual policy comparison asks which of two pricing policies would have produced the better outcome. No ground truth exists for policies that were never run. Practitioners increasingly substitute an LLM customer population for the missing counterfactual, then rank policies by the simulated outcome.

Two conventions dominate.

| Convention | What the model returns | Representative work |
|---|---|---|
| Numeric | Purchase probability per persona | Huang and Wang (2026) |
| Discrete | Accept or reject a price | Deployed agent simulations |
| Discrete + reason | Accept or reject plus a code | This work |

The choice is treated as an implementation detail. It is not. A probability is a model belief that must be calibrated. A decision is a sample whose frequency becomes the distribution without calibration. These are different statistical objects, and they fail differently.

### 1.2 Gap

Prior work holds one convention fixed and evaluates something else.

| Work | Convention | Evaluated against |
|---|---|---|
| Huang and Wang (2026) | Numeric | Predictive fit on H&M sales |
| Zhu and Chang (2026a) | None (no LLM customers) | Trace alignment |
| Zhu and Chang (2026b) | None | Policy repair quality |
| Zhu and Chang (2026c) | None | Trace diagnosability |
| Zhang et al. (2025) | Numeric choice | Parameter recovery |
| Kireyev (2026) | Numeric choice | Preference recovery |
| Lei (2026) | Discrete (seller side) | Negotiation profit |

No study varies the convention under a fixed population and a reference ranking.

### 1.3 Contributions

1. **A ground-truth-anchored protocol.** We define ranking fidelity as the Spearman correlation between the policy ranking induced by a simulator and the ranking implied by an analytic demand model. This separates model error from sampling noise and from small true effects, which predictive-fit metrics conflate.

2. **A controlled comparison of three output contracts at equal budget.** We report accuracy, trace alignment, and a cost-to-stability measure that captures the repeats a discrete contract needs to recover a distribution.

3. **A power analysis for contract comparison.** We quantify how many seeds a policy-ranking comparison needs before a three-point difference is resolvable. [REVISED IN v1 — the crossover framing measured in the oracle did not hold.]

Contribution 3 is the paper if it holds. If both contracts behave identically, the honest report is a null result and the framing changes (Section 7.2).

### 1.4 Non-claims

We do not claim to originate any of the following. Each is attributable to prior work, and we say so in the text rather than in a footnote.

| Claim | Prior work |
|---|---|
| LLM choices require calibration | Zhang et al. (2025) |
| Persona mixtures recover demand distributions | Huang and Wang (2026) |
| Trace statistics beat outcome metrics | Zhu and Chang (2026a) |
| Alignment can improve while revenue falls | Zhu and Chang (2026b) |
| Traces can be undiagnosable, so abstain | Zhu and Chang (2026c) |
| Thresholds should be preregistered and frozen | Zhu and Chang (2026c) |
| Depth and width have non-monotone returns | Dang et al. (2025) |

---

## 2. Related Work

### 2.1 LLM demand simulators

Huang and Wang (2026) represent customers as a finite mixture of personas, elicit a purchase probability per persona and candidate price, and aggregate with calibrated mixture weights to form a demand distribution. They evaluate on an online fashion dataset and report predictive performance under expected-revenue and CVaR objectives. Their output is a full distribution; ours is a direction and an abstention.

Zhang et al. (2025) show that uncorrected LLM choices inflate demand-parameter error and that a correction fitted on 10% of human data reduces it. This motivates our B1 baseline and constrains our claim: calibration is not a contribution.

Kireyev (2026) recovers price, quality, and brand preferences of 28 LLMs from 3,600 New York hotel booking tasks using a logit choice model. Price sensitivity spans more than an order of magnitude and mean booked nightly price ranges from about 247 to 393 USD on identical tasks. This sets the heterogeneity range in our A8 ablation and supports the premise that an uncalibrated LLM customer is not interchangeable with another.

Lei (2026) benchmarks LLM **sellers** in hidden-preference vehicle negotiations. Deal rates exceed 0.99 while profit stays near a random baseline. We cite this only as an inference from the seller side; it is not evidence about LLM customers.

### 2.2 Trace-based evaluation and abstention

Zhu and Chang (2026a) study a two-hotel revenue-management simulator in which a learning agent reaches near-reference RevPAR while failing to learn market-like yield management. They introduce a trace protocol over RevPAR, occupancy, ADR, price-bucket distributions, and L1/JS distances. Their central observation, that higher exact action accuracy can worsen aggregate trace alignment, is reproduced in our A2 ablation, not claimed as ours.

Zhu and Chang (2026b) audit policy repair in a hotel pricing simulator where an agentic editor receives only region-level diagnostic feedback. A tree editor attains stronger pooled alignment and a better reference-state distance while revenue falls. We cite this as the strongest existing evidence that alignment and outcome can move apart.

Zhu and Chang (2026c) treat entry into trace interpretation as a diagnosability decision and abstain when the trace cannot support the claim. They state explicitly that they do not claim to originate diagnosability, abstention, overlap analysis, shift detection, or behavioral diagnostics. We adopt their exposure construct: affected traffic, not nominal cell count, predicts diagnosability.

### 2.3 Persona generation mechanics

Agent Hospital (Li et al., 2025) establishes the simulacrum-plus-evolution pattern and the requirement that evolution needs verifiable labels. Patient-Zero (Lai et al., 2026) separates attribute selection from text generation, adds a dual-track memory, and reports that unstructured narrative personas align worse than a static structured schema. We adopt these mechanics and reproduce their ordering in A3 and A4.

Dang et al. (2025) report that orchestration depth and width have non-monotone returns and that learned orchestrators concentrate traffic on few hubs. We cap consultation depth and monitor per-department call share; A9 tests whether the non-monotonicity holds here.

---

## 3. Method

### 3.1 Ground truth

We fix an analytic demand model so that every policy has an exact expected revenue and the policy ranking is unique.

```
v_i = α − ρ p_i + η m
P(hotel) = exp(I) / (1 + exp(I)),   I = μ log Σ_j exp(v_j / μ)
P(i | hotel) = exp(v_i / μ) / Σ_j exp(v_j / μ)
E[demand_i] = M · P(hotel) · P(i | hotel)
```

Capacity 100, horizon 30 days, seven price buckets over 100-220, and μ = 0.5 follow the published specification of the two-hotel simulator (Zhu and Chang, 2026a). The values of α, ρ, and η are not published in the sources we could access; we recalibrate them and report that this makes B2 a coordinate alignment, **not a reproduction of their numbers**.

Nine policies form a 3 × 3 grid over occupancy band and booking lead time, giving 36 ordered pairs. The unit of analysis is the pair.

### 3.2 Output contracts

| Contract | Model returns | Distribution obtained by |
|---|---|---|
| A | Purchase probability in [0,1] | Direct read |
| B | Accept / reject | Repeated sampling |
| C | Accept / reject + reason code | Repeated sampling |

Contracts B and C therefore pay a repeat cost that A does not. This cost is the object of the cost-to-stability metric, not a nuisance.

### 3.3 Shared simulator

All contracts share the population, the persona sampler, the memory, and the aggregation layer, so that only the reporting convention varies.

- Stratified attribute sampling in code, not in the prompt.
- Rejection sampling for infeasible attribute combinations.
- Dual-track memory with a three-valued consistency gate.
- Deterministic aggregation in the event queue.

### 3.4 Metrics

| Metric | Definition |
|---|---|
| Ranking fidelity | Spearman correlation with the analytic ranking over 9 policies |
| Direction accuracy | Sign agreement over 36 policy pairs |
| cost-to-stability | LLM calls until the ranking is unchanged over 3 consecutive checkpoints |
| Trace distance | L1 over 7 price buckets, range 0-2, per cell |
| Abstention rate | Fraction of comparisons returned as indeterminate |

Checkpoints are placed at 10% increments of the call budget. Intervals are seed-level cluster bootstrap with 2,000 draws; the 36 pairs from one seed are not treated as independent.

### 3.5 Preregistered decisions

The following table is fixed before data collection and hashed. It is the only rule by which results will be interpreted.

| Outcome | Interpretation |
|---|---|
| B matches A on fidelity with lower cost | Numeric prohibition justified |
| A dominates on fidelity and cost | Current design withdrawn |
| Crossover across heterogeneity levels | Interaction is the finding |
| All contracts equivalent | Null result; framing revised |

### 3.6 Falsifiers

Each component carries an explicit condition under which we withdraw it.

| Component | Withdrawn if |
|---|---|
| Abstention gate (A5) | Gate produces **0 wrong conclusions** |
| LLM customer layer (B1) | A **10% calibrated logit** matches our direction accuracy |
| Contract difference (A1) | Pilot shows no divergence |
| Heterogeneity result (A8) | All contracts collapse at 10× |

### 3.7 Statistical power

Direction accuracy over 36 policy pairs has a one-measurement standard error
of 0.050 at a true rate of 0.9, so a three-point contract gap is invisible in
a single run. An offline check with an oracle backend over 24 seeds found a
seed-level standard deviation of 0.035 to 0.053. Resolving a three-point gap
at 95% confidence therefore requires at least 24 seeds.

Every contract comparison is reported as a seed-level mean with a cluster
bootstrap interval. No single-run point estimate is reported as a result, and
a sign change between adjacent heterogeneity levels is not evidence of
crossover unless the interval excludes zero on both sides.

---

## 4. Experiments

### 4.1 Pilot gate

Two policies, one price, 40 personas, contracts A and B, ten repeats. We count how often the pairwise ranking flips.

| Pilot result | Action |
|---|---|
| Both stable 10/10 | Stop; **no paper** |
| Only B unstable | A dominates; design unjustified |
| Only A unstable | Proceed |
| Both unstable | Search for heterogeneity condition |

### 4.2 Baselines

| ID | Baseline | Attack defended |
|---|---|---|
| B0 | Analytic logit | Accuracy has no meaning without a reference |
| B1 | 10% calibrated logit | LLM unnecessary |
| B2 | Two-hotel reimplementation | Trace scale incomparable |
| B3 | Persona mixture, numeric elicitation | State of the art is better |
| B4 | Bootstrapped behavioral cloning | Trace gain is an artifact |
| B5 | Uniform random policy | Everything correlates |

### 4.3 Ablations

| ID | Variation | Isolates |
|---|---|---|
| A1 | Contracts A / B / C | Main effect |
| A2 | Sampling vs argmax | Deterministic collapse |
| A3 | Code vs LLM attribute generation | Distribution control |
| A4 | Dual-track memory on/off | Persona stability |
| A5 | Trace gate on/off | Value of abstention |
| A6 | Exposure = traffic vs cell count | Gate denominator |
| A7 | Calibration fraction 0/5/10/50% | Marginal value of calibration |
| A8 | Heterogeneity 1× / 3× / 10× | External validity |
| A9 | Consultation depth 0 / 1 / 2 | Multi-agent value |

### 4.4 Results

[TABLE 1 — Contract main effect: fidelity, direction accuracy, cost-to-stability, abstention]

[TABLE 2 — Interaction: contract × heterogeneity; report the gap with a confidence interval, not a crossover flag]

[TABLE 3 — Gate value: wrong conclusions with and without the gate]

---

## 5. Threats to Validity

| Threat | Effect | Mitigation |
|---|---|---|
| Synthetic only | No claim about real hotels | Stated in abstract and conclusion |
| α, ρ, η unpublished | B2 not a reproduction | Reported as coordinate alignment |
| Huang and Wang procedure partial | B3 is a comparable implementation | No performance claim against them |
| One demand family | Narrow external validity | Heterogeneity sweep reported |
| Ranking fidelity is not profitability | Fidelity may not transfer to revenue | Framed as comparison validity only |

---

## 6. Ethics and Reproducibility

The study uses synthetic populations only. No client data, no personally identifiable information, and no decisions about individuals are produced or evaluated.

We plan to release prompts, seeds, the ground-truth construction, and the preregistration hash. Cited works are used by citation only; the arXiv versions of the trace-diagnostic papers carry a perpetual non-exclusive license, so no figures or tables are reproduced. PriceBench releases tasks and response sets, and PrefBench releases code, both of which we use as external calibration anchors rather than as data for our own claims.

---

## 7. Discussion

### 7.1 What would change the conclusion

If the discrete contract recovers the analytic ranking at equal or lower cost, the numeric-prohibition design in deployed systems is over-conservative. If it requires an order of magnitude more calls, the prohibition is justified and the burden shifts to making probability reporting calibratable.

### 7.2 If the result is null

We will report equivalence as the finding and drop the interaction claim. A well-powered null on a question practitioners treat as settled is publishable at a workshop; an unsupported crossover is not.

---

## 8. Limitations

The ground truth is analytic, so it cannot validate the demand specification itself. All evidence comes from one simulator family. The cost-to-stability metric depends on the checkpoint schedule and on the model's sampling temperature. Results are conditional on the three contracts described; other reporting formats may behave differently.

---

## References

[1] C. Huang, K. Wang. LLM-Powered Virtual Population for Demand Simulation and Pricing. arXiv:2606.16183, 2026.

[2] P. Zhu, S. Chang. Market-Alignment Risk in Pricing Agents: Trace Diagnostics and Trace-Prior RL under Hidden Competitor State. arXiv:2605.06529, 2026. (2026a)

[3] P. Zhu, S. Chang. When Aggregate Alignment Misleads: Auditing Policy Repair Without Per-State Expert Actions. arXiv:2607.03386, 2026. (2026b)

[4] P. Zhu, S. Chang. When Are Aggregate Agent Traces Diagnosable? Traffic-Governed Interpretation and Calibrated Abstention. arXiv:2609.25806, 2026. (2026c)

[5] B. Zhang, J. Li, A. Hortaçsu, X. Ye, V. Chernozhukov, A. Ni, E. W. Huang. Agentic Economic Modeling. arXiv:2510.25743v4, 2026.

[6] P. Kireyev. PriceBench: A Diagnostic Benchmark for Price, Quality, and Brand Preferences in LLM Booking Agents. arXiv:2609.31468, 2026. EMNLP 2026 Industry Track.

[7] Y. Lei. PrefBench: Evaluating Zero-Shot LLM Agents in Hidden-Preference Personalized Pricing Negotiations. arXiv:2605.22855, 2026.

[8] J. Li, Y. Lai, W. Li, et al. Agent Hospital: A Simulacrum of Hospital with Evolvable Medical Agents. arXiv:2405.02957v3, 2025.

[9] Y. Lai, Z. Wang, W. Ma, Y. Liu. Patient-Zero: Scaling Synthetic Patient Agents to Real-World Distributions without Real Patient Data. arXiv:2509.11078v2, 2026.

[10] Y. Dang, C. Qian, X. Luo, et al. Multi-Agent Collaboration via Evolving Orchestration. NeurIPS 2025. arXiv:2505.19591v2.

---

## Appendix A. Open items before submission

| Item | Owner | Status |
|---|---|---|
| Recalibrate α, ρ, η | — | Open |
| Decide B3 fidelity level | — | Open |
| Fix checkpoint schedule | — | Open |
| Preregistration hash | — | Blocked on Sections 3.4-3.6 |
| Venue and page limit | — | Open |
| arXiv check for new Zhu and Chang work | — | Open |
