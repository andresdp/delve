# Validating Delve: Replication and Human-Subject Studies

This document collects two related but distinct validation efforts discussed for Delve:
(1) approximating Mary Shaw's original design-space case study as a sanity check on the
mining pipeline, and (2) using undergraduate software-design-course students as a source
of real, independent human design data to validate and evaluate Delve empirically. Both
are currently **proposals** — nothing here has been implemented or run yet.

---

## Part 1 — Approximating Mary Shaw's Original Experiment

### What's actually available

- **The original task prompt is still live.** Shaw's case study gave three independent
  teams the same design problem (a traffic-signal-style controller specification) and
  compared the design spaces each team implicitly worked within. The prompt document
  itself is still publicly reachable, so it can be used verbatim as the `use_case` /
  seed context for a Delve run.
- **The original teams' work is not recoverable.** The three teams' actual transcripts,
  working notes, or recorded sessions from Shaw's study are not publicly available (the
  workshop's public materials stop at the prompt itself). This means a literal
  replication — feeding Delve the same raw data Shaw's teams produced — is not possible.

Because of that gap, a full replication isn't feasible, but a *reasonable approximation*
is, structured as two tiers of increasing authenticity.

### Tier 1 — Real prompt + synthetic personas + a real reference tool

- Use the real, original task prompt as the shared problem statement.
- Construct several synthetic "team" personas that mirror the kind of divergent thinking
  styles Shaw observed across her three real teams (e.g. one leaning toward a
  centralized/monolithic controller design, one toward a distributed/event-driven design,
  one toward a configuration-driven/rules-engine design) — not cosmetic labels, but
  distinct design philosophies that would plausibly produce different dimensions.
- Ground at least one persona's output against a real, modern reference implementation
  or tool in the same problem space (e.g. an open-source traffic/signal-control system,
  or an analogous state-machine/rules-engine project such as SUMO) rather than relying
  purely on LLM-generated "designs," so at least one data source isn't synthetic
  end-to-end.
- This tier is explicitly a **proxy**, not a replication: it substitutes synthetic
  divergence for real inter-team divergence. Its value is as a first, cheap sanity check
  that Delve's mining pipeline can recover a design space with a *known, real* problem
  statement and *plausible* alternative solution philosophies.

### Tier 2 — Real, independently-produced data (different problem, real teams)

- Rather than reconstruct Shaw's exact problem, use data that is genuinely produced by
  independent human teams solving *some* shared design problem — e.g. student capstone
  project reports, or design-rationale documents from independent open-source projects
  solving the same class of problem.
- This trades exact fidelity to Shaw's original problem for authenticity of the
  underlying data: real independent designers, real design trade-offs, real documents —
  just not Shaw's specific traffic-signal exercise.
- This tier is a natural bridge to Part 2 below, since a software-design course is
  exactly this kind of source, and can be set up deliberately (same prompt, independent
  teams) rather than found opportunistically.

### Concrete Delve workflow (either tier)

1. Tag every input document with a provenance prefix identifying which persona/team/source
   it came from (e.g. `team-a__doc1`, so provenance survives ingestion).
2. Set `use_case` in the run config from the real task prompt's actual problem statement,
   not a paraphrase, so the open-coding stage is grounded in the authentic problem framing.
3. Run Delve at least twice for comparison: once with `max_num_clusters` constrained to
   roughly Shaw's reported dimension count (~7), and once unconstrained (`null`), to see
   how much the recovered structure is an artifact of the cap versus the data.
4. Reconstruct a "Table 1"-style comparison by grouping the `label_documents` output by
   source/provenance prefix — this shows, per team/persona, which dimensions and values
   their documents actually activated, mirroring the structure of Shaw's own team-by-team
   table.
5. Compare the reconstructed table against Shaw's actual reported dimensions (count,
   names, degree of independence between dimensions) — not to claim statistical
   equivalence, but as an **interpretive lens**: where does Delve's mined structure look
   structurally similar to Shaw's (e.g. similar number of dimensions, similar mix of
   independent vs. non-independent dimensions), and where does it diverge, and why?

### Caveats

- Tier 1's synthetic personas are a stand-in for real inter-team divergence; any
  agreement between Delve's mined space and Shaw's reported one is suggestive, not
  confirmatory, until tested against real independent data (Tier 2 or Part 2).
- A single reference implementation is a thin ground truth; treat matches/mismatches
  against it as anecdotal evidence, not validation.
- The goal of this exercise is a plausibility check and a talking point for a research
  presentation, not a claim of formal replication.

---

## Part 2 — Empirical Validation with Undergraduate Students

Three study designs were proposed for validating Delve using students in a final-year
software design course, organized in groups: (1) have groups independently solve the
same design exercise, then run Delve on their outputs; (2) present Delve-generated
design spaces to students and collect feedback; (3) some form of A/B study. These are
not competing alternatives — they validate different things and are best run in
sequence.

### Option 1 — Student groups solve the exercise, then Delve mines the outputs

This is the closest authentic analogue to Shaw's own study design: multiple independent
human teams solving an identical problem, without the compromises Tier 1 above requires.
A course section with, say, eight to ten groups also improves on Shaw's original three
teams statistically — it becomes possible to ask whether a dimension Delve surfaces
recurs across most teams' designs, or is an artifact of one team's specific phrasing,
which three data points can't reliably distinguish.

This also directly instantiates the **pattern-confirmation** step from the computational
grounded theory literature (Nelson 2020): a pattern the LLM pipeline detects should be
confirmed (or refuted) via an independently different method. Independently-produced
human team designs are exactly that independent method — a much stronger check than
comparing two LLM personas against each other.

**What this validates:** whether Delve's mining process correctly recovers a design
space that is present in real, independently-produced human design artifacts — i.e. the
construct validity of the mining pipeline itself.

**Practical notes:** this is comparatively low-cost, since the course likely already
produces this material as coursework; it just needs the exercise designed so that groups
work independently (no shared design discussion across groups) and their submissions are
collected and lightly structured (per-team documents, tagged with provenance) so they can
be fed into Delve the same way Tier 1/2 documents above would be.

### Option 2 — Present Delve-generated design spaces to students for feedback

This tests something different from Option 1 and should not be treated as a substitute
for it: it evaluates the comprehensibility and perceived usefulness of the **output
artifact**, not whether the mining process got the design space right. A design space
could be rated as clear and compelling by students while still being wrong, or correct
but confusing — so on its own, this option doesn't validate mining fidelity.

Its real value is as a **follow-on to Option 1, with the same students**: after a team
has submitted its own design, show them the space Delve mined from all teams'
submissions (including their own) and ask two things — does this match what your team
actually considered, and does it surface alternatives you didn't think of? This is a
form of respondent validation (member checking), a standard qualitative-methods move,
and it directly tests Shaw's own claim about what a design space is *for*: that it
"inoculates designers against the temptation to use the first alternative that comes to
mind." Asking students whether seeing the mined space would have changed their approach
is a direct empirical probe of that claim.

**What this validates:** usability/comprehensibility of the output artifact, and
(via the "would this have changed your approach" framing) a first empirical signal for
Shaw's inoculation claim — but not the correctness of the mining process.

### Option 3 — A/B study

Most rigorous in principle, most expensive to do well, and best treated as a stretch
goal for a later course offering rather than the first move, once Option 1 has shown
what a typical Delve-mined design space for the exercise actually looks like.

The key design decision is *what* is being compared and *when* the design space is
introduced:

- **Timing risk:** handing the mined design space to one group *before* they design
  risks measuring whether students copy a handed-to-them dimension list rather than
  measuring anything about design quality — a real confound, not a hypothetical one.
- **Cleaner alternative:** give the mined space to one group only *after* they've
  drafted their own design, framed as a gap-check ("which of these dimensions did you
  consider, which did you miss") rather than a design aid used during drafting.
- **Outcome measure:** prefer a coverage / alternative-awareness measure (how many
  distinct dimensions/values the group considered or explicitly rejected) over a
  holistic quality score, which is more exposed to grader bias. This also ties directly
  back to Shaw's "first alternative" framing — the outcome of interest is breadth of
  alternatives considered, not just whether the final design is "good."
- **Logistics:** needs two matched cohorts or course sections, a coverage rubric agreed
  in advance, and ideally blind grading (graders not knowing which group saw the mined
  space).

**What this validates:** a causal claim about outcomes — does access to a Delve-mined
design space change design behavior for the better — which is the strongest claim of
the three options, but only if the confounds above are designed out up front.

### Recommended sequencing

1. **This semester:** run Option 1. It is low-cost (the course likely already produces
   this coursework), and it answers the prior question of whether Delve is mining
   something real, using authentic independent human data instead of synthetic personas.
2. **Same semester, same students:** add a lightweight version of Option 2 immediately
   after — one additional class session showing groups the mined space and collecting
   structured feedback (does it match what you considered / would it have changed your
   approach). Cheap to add once Option 1's data exists.
3. **A later offering:** design Option 3 properly as its own study, once Option 1 has
   shown what a "typical" mined design space looks like for this exercise — that makes
   the outcome measure and rubric much easier to specify than designing it blind.

### Practical / ethical notes

- Even though this is coursework, using student submissions and feedback as research
  data (especially if any of it is intended for publication) should go through the
  institution's ethics/IRB process, and should be set up for informed consent and
  anonymization from the start rather than retrofitted afterward.
- Running the same exercise across multiple semesters, with consistent provenance
  tagging, naturally builds a growing multi-team corpus — giving more statistical
  confidence in recurring dimensions than Shaw's original three teams could support,
  without needing a single very large one-off study.
