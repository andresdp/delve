---
title: deepeval GEval's Default temperature=0.0 Rejected by Newer OpenAI Judge Models
date: 2026-09-05
category: integration-issues
module: evaluation
problem_type: integration_issue
component: service_layer
symptoms:
  - "GEval judge calls fail with `Error code: 400 - {'error': {'message': \"Unsupported value: 'temperature' does not support 0.0 with this model. Only the default (1) value is supported.\", 'type': 'invalid_request_error', 'param': 'temperature', 'code': 'unsupported_value'}}`"
  - "`run_scoreboard` degrades to `{\"unavailable\": true, \"error\": ...}` for every criterion on every run, with only a WARNING-level log line — the pipeline itself completes normally, so the failure is easy to miss"
  - "The failure is 100% reproducible with a configured judge model from a newer, reasoning-tier OpenAI family (e.g. a GPT-5-class model), and did not occur with older models (e.g. gpt-4o-mini)"
root_cause: wrong_api
resolution_type: code_fix
severity: medium
tags: [deepeval, geval, openai, temperature, judge-model, evaluation-scoreboard, taxonomy-generator]
---

# deepeval GEval's Default temperature=0.0 Rejected by Newer OpenAI Judge Models

## Problem

`src/taxonomy_generator/evaluation/metrics.py`'s `build_metrics()` passed a bare OpenAI model-name string to `GEval(model=...)`. `GEval` then lets deepeval construct its own internal `OpenAIModel` for that string, and `OpenAIModel.__init__` defaults `temperature` to `0.0` whenever neither an explicit `temperature` nor `settings.TEMPERATURE` is set (verified by reading `deepeval/models/llms/openai_model.py` at the installed version — `deepeval==4.1.8`). Newer, reasoning-tier OpenAI models (the configured judge here was a GPT-5-class model, `gpt-5.6-luna`, resolved from `evaluation.judge_model` falling back to `models.model`) reject any `temperature` value other than the API default of `1` — they don't support `temperature=0` at all, unlike older chat models (`gpt-4`, `gpt-4o-mini`, etc.), which accept the full range including `0`. (`deepeval/models/llms/openai_model.py` here refers to the installed `deepeval` package's own source, not a file in this repo — inspected directly in the `taxonomy` conda environment's `site-packages` to confirm the default.)

This surfaced only now because `evaluate_taxonomy` — the node that calls `run_scoreboard` → `build_metrics` — was itself dead code in `graph.py` until this session's branch wired it in for the first time on a live run (see the related architecture-pattern doc below for that discovery). The bug had been latent since the evaluation suite was first built.

## Symptoms

- `Error code: 400 - {'error': {'message': "Unsupported value: 'temperature' does not support 0.0 with this model. Only the default (1) value is supported.", 'type': 'invalid_request_error', 'param': 'temperature', 'code': 'unsupported_value'}}`
- Every GEval criterion in the scoreboard reports `unavailable: true`; the scoreboard's `criteria` list is empty.
- The enclosing pipeline run **does not fail** — `run_scoreboard`'s `try/except` degrades to the unavailable shape by design (R7 in the evaluation suite's plan), so this can run unnoticed in production-style runs unless someone is specifically watching the WARNING log line or the scoreboard content.

## What Didn't Work

Nothing was tried before identifying the root cause directly — the 400 error's message names the exact offending parameter and value, so the fix path was clear once the error was visible for the first time (which itself only happened after wiring `evaluate_taxonomy` into the graph on a live run — see Related).

## Solution

`src/taxonomy_generator/evaluation/metrics.py` now imports the model class directly and constructs one explicit instance with `temperature=1.0`, passed to every `GEval` in the loop instead of the bare model-name string:

```python
from deepeval.models import OpenAIModel

def build_metrics(model, threshold, include_coverage):
    ...
    # deepeval's OpenAIModel defaults to temperature=0.0, which newer
    # reasoning-tier models (e.g. gpt-5.x) reject outright ("Only the
    # default (1) value is supported"). temperature=1.0 is valid for both
    # older and newer OpenAI models, so it is used unconditionally here
    # rather than special-casing by model name.
    judge_model = OpenAIModel(model=model, temperature=1.0)

    metrics = []
    for criterion in criteria:
        metric = GEval(
            name=criterion.name,
            criteria=criterion.criteria,
            evaluation_params=[SingleTurnParams.INPUT, SingleTurnParams.ACTUAL_OUTPUT],
            threshold=threshold,
            model=judge_model,   # an OpenAIModel instance, not a bare string
            async_mode=True,
        )
        ...
```

Verified with a live API smoke test against the configured judge model, returning a real score and rationale instead of the 400.

## Why This Works

`temperature=1.0` is the literal API default OpenAI's own error message names as the only supported value for these models, and it is also a valid value in the full range accepted by older chat models — so passing it explicitly is a universal fix with no model-name branching required. The underlying issue was never *which* model to call, but *how* it was invoked: letting `GEval` build its model implicitly from a bare string hands control of `temperature` to deepeval's own default, which this project's config never intended to rely on. Constructing the `OpenAIModel` explicitly makes that parameter a first-class, deliberate choice instead of an implicit one.

## Prevention

- When wrapping a third-party judge/scoring library (deepeval, or similar) around a model your project's config selects, **construct the underlying model object explicitly** rather than passing a bare model-name string through — implicit construction hands you whatever defaults the library chose, which may not hold for every model family the project might configure.
- Reasoning-tier OpenAI models (o1/o3/GPT-5-class) as a general rule accept **no** `temperature` override — treat `temperature=1.0` (the API default) as the safe universal choice unless you specifically need to branch by model family.
- Because this pipeline's evaluation node is deliberately fault-tolerant (never fails the run, only degrades to `unavailable`), an integration bug here is *silent* — it will not appear as a crash or a failing test. When adding or changing a judge-model integration, do a live smoke test against the actual configured production judge model (not just a default/dev one) before trusting that the feature works end to end, since a purely-mocked or offline test suite would never have caught this API-shape mismatch.

## Related Issues

- `docs/solutions/architecture-patterns/taxonomy-evaluation-suite-scoreboard-and-consistency.md` — the evaluation suite this bug lives in; that doc's postscript records how `evaluate_taxonomy` came to run for the first time and surfaced this bug.
- Fixed on branch `feat/taxonomy-evaluation-feedback-integration` (commit `83dacf2` as of this writing, pushed to `origin`, PR not yet opened).
