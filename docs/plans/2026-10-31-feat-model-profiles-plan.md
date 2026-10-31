---
title: "feat: model profiles — several LLM providers and models in one pipeline run"
type: feat
status: proposed (2026-10-31)
date: 2026-10-31
related: >-
  src/taxonomy_generator/{settings,configuration,utils,pipeline_cli,tool_update}.py,
  src/taxonomy_generator/nodes/*.py, src/taxonomy_generator/evaluation/{judge,runner,consistency}.py,
  src/delvedspace/{workspace,chat,point,wiki_build}.py, src/delvedspace/templates/ddspace.yaml,
  docs/plans/2026-10-15-refactor-taxonomy-data-layer-plan.md (U0, the record/replay cache),
  docs/plans/improvements.md
---

# Model profiles

## Goal

Let one pipeline run (one LangGraph graph instance) use **several providers and models**:

- a different model per node, for example a cheap model for open coding and a stronger one for building the
  taxonomy;
- a different provider per role, for example OpenAI to generate, Anthropic to judge, and a local Ollama model to
  summarize;
- per-model settings, such as temperature, reasoning effort, a base URL for local servers, and the environment
  variable that holds the key.

It is also the basis for personas that each use their own LLM (the multi-persona plan, in
`DESIGN_SPACE_ROADMAP.md`).

With no new settings, every run behaves exactly as today.

## Current state (2026-10-31)

- **Model names.** `load_chat_model("provider/model")` wraps LangChain's `init_chat_model`
  ([utils.py:73](../../src/taxonomy_generator/utils.py)). Any provider LangChain supports works today, but only
  with the provider's default settings and environment variables.
- **Roles.** `ModelSettings` has three LLM roles plus the embedding model
  ([settings.py:36](../../src/taxonomy_generator/settings.py)):
  - `generation_llm`: open coding, summaries, generate/update/review, consolidation, merging, selection,
    labeling and the report;
  - `evaluation_llm`: the scoreboard, consistency adjudication and the saturation critic;
  - `matching_llm`: ground-truth matching.

  A warning fires when two roles share a model.
- **Call sites.** About 25 calls in 13 modules read `configuration.<role>_llm` directly; every pipeline node
  uses `generation_llm`.
- **Embeddings.** `load_embeddings_model` supports `openai/` and `ollama/` only.
- **Portability.** Structured output (`with_structured_output`) and tools mode (`bind_tools`, parallel tool
  calls) assume a capable, OpenAI-like model. Small local models often fail at both.
- **Token accounting.** `TokenTracker` sums tokens over all calls without recording which model made them. The
  CAIN study prices tokens per model with its own `rates.yaml`.

## Design

### KTD1. Named profiles, and roles and nodes that point at them

```yaml
models:
  profiles:
    fast:   {model: openai/gpt-5.4-nano}
    strong: {model: anthropic/claude-sonnet-5-5, temperature: 0}
    local:  {model: ollama/qwen3:4b, base_url: http://localhost:11434}
    judge:  {model: openai/gpt-5.4-mini, reasoning_effort: low}
  # Roles, as today. A role takes a profile name or a provider/model string.
  generation_llm: strong
  evaluation_llm: judge
  matching_llm: openai/gpt-4.1-mini
  embedding: openai/text-embedding-3-small
  # Optional per-node overrides; a node without one uses its role.
  nodes:
    open_code_minibatch: fast
    summarize: local
```

- **Profile fields:**
  - `model` (required, `provider/model`);
  - `temperature`, `max_tokens`, `reasoning_effort`, `base_url`;
  - `api_key_env`: the name of the environment variable to read, never the key itself;
  - `structured_output`: `auto`, `json_schema`, `function_calling` or `json_mode`;
  - `extra`: passed through to `init_chat_model`.
- **Old configs.** A plain `provider/model` string works anywhere a profile name does, so existing configs and
  `ddspace.yaml` files keep working.
- **Node names.** The `nodes:` keys are the LangGraph node names. Unknown names are an error at load time, with
  the list of valid names.

### KTD2. One resolver, `model_for(configuration, node)`

- `model_for` returns the chat model for a node: the node override, else the node's role, then the profile, then
  `init_chat_model` with the profile's settings.
- Models are cached per profile for the run.
- Every call site that reads `configuration.<role>_llm` switches to `model_for`. The role of each node is
  declared in one table, the same mapping the `ModelSettings` docstring describes.

### KTD3. Capabilities are checked, not assumed

- Each node declares what it needs: structured output, tools or parallel tools.
- At startup, the resolver checks each node's profile against a small capability table: known providers, plus
  per-profile flags such as `tools: false`. It refuses a run that would put tools mode on a model without
  tool calling, before any call is made.
- Structured output uses the profile's `structured_output` method. `auto` keeps today's behaviour for OpenAI.

### KTD4. Usage and cost per profile

- `TokenTracker` records tokens per model (from `response_metadata["model_name"]`, falling back to the profile).
- Prices come from an optional `rates:` block (USD per 1M input, cached-input and output tokens). It has the same
  shape as the study's `rates.yaml`, which then becomes one instance of it.
- The run file's `run_metrics` gains `by_model: {model: {tokens…, cost}}`.

### KTD5. The independence warning becomes per profile

- `shared_llm_warnings` compares resolved models, not role strings. It warns when a judging role (evaluation or
  matching) resolves to the same model as any generating node.
- Personas that share a model are allowed; the persona plan reports it.

### KTD6. Works with the record/replay cache

The data-layer plan's U0 cache keys on (resolved model, profile settings, prompt hash). A profile change
therefore never replays a stale answer.

## Implementation units

| Unit | What | Files |
|---|---|---|
| P1 | Profiles in `ModelSettings` and `configuration.py` (parse, validate, and accept plain strings); the node-to-role table | `settings.py`, `configuration.py` |
| P2 | `model_for` and the profile-aware `load_chat_model`; switch the call sites node by node; the old role-based calls stay valid during the switch | `utils.py`, `nodes/*.py`, `evaluation/*.py`, `report_renderer.py` |
| P3 | Capability check and structured-output method per profile | `utils.py`, `tool_update.py` |
| P4 | Usage and cost per model in `TokenTracker` and `run_metrics`; the `rates:` block | `pipeline_cli.py`, `settings.py` |
| P5 | Embedding profiles (any LangChain embedding provider, with `base_url`) | `utils.py` |
| P6 | `ddspace`: the `models:` block in the template (profiles commented out); `ddspace ask` and `point` take a profile name; `ddspace check` lists the resolved model of each node | `templates/ddspace.yaml`, `chat.py`, `point.py`, `check.py` |
| P7 | Docs: `SETTINGS.md`, `USAGE.md`, `CONCEPTS.md` ("Model profile") | docs |

## Verification

- **No change for existing configs:**
  - each paper config (C1–C3) and the `ddspace` template resolve every node to the same model as today, by unit
    test over the resolver;
  - a replayed C1 run, with the U0 cache, gives identical output.
- **Per-node override:** a unit test with a fake chat model checks that `open_code_minibatch` uses its override
  and the other nodes use their role.
- **Mixed-provider smoke run:** one small corpus with OpenAI generation, an Ollama summarizer and a different
  judge. It must finish, with `by_model` showing three models.
- **Refusal:** tools mode on a profile flagged `tools: false` is refused before the first call.

## Risks

| Risk | Mitigation |
|---|---|
| Provider differences in structured output break parsing | Per-profile `structured_output`; existing parse fallbacks; the capability check |
| Config complexity for simple users | Profiles are optional; plain strings keep working; the template keeps profiles commented out |
| Keys in config files | Only `api_key_env` (a variable name) is accepted; a literal key is rejected |
| Silent cost growth with strong models on high-volume nodes | `by_model` cost in the run summary; `ddspace check` shows what each node uses |

## Open questions

1. Should profiles also allow fallbacks (try `local`, then `fast` on failure)? Not in the first version.
2. Should `ddspace init` ask for profiles, or keep asking for one generation and one evaluation model?
