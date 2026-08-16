---
type: public API
title: Public Python API and package surfaces
description: Supported package exports, graph invocation contract, packaging entrypoints, and boundaries around internal implementation modules.
tags: [api, packaging, python]
---

# Public Python API and package surfaces

## Supported imports

`taxonomy_generator.__all__` exports `graph`, `Configuration`, `Settings`, `init_settings`, `State`, `InputState`, `OutputState`, `Doc`, `UserFeedback`, `strings_to_docs`, and `docs_from_dicts`. The intended programmatic path is:

```python
from taxonomy_generator import Doc, graph, strings_to_docs
result = await graph.ainvoke({"documents": strings_to_docs(texts)})
```

Input documents may be `Doc` objects or dictionaries accepted by `docs_from_dicts`; `InputState` is typed as `List[Doc]`, while the implementation deliberately normalizes dictionaries and strings, so the practical contract is broader than the annotation. File-mode JSON objects do not preserve their IDs because `main.load_corpus` extracts only `content` before `strings_to_docs`; direct programmatic `docs_from_dicts` does preserve supplied fields. Output contains `documents`, `clusters`, `explanations`, and `messages` as defined in [State and schemas](../data-model/state-and-schemas.md). The final taxonomy is the last element of `clusters`; final document categories and scores are on `documents`.

## Runtime and packaging surfaces

`pyproject.toml` installs the `delve` console script (`main:main`), discovers packages below `src`, and includes `py.typed` package data. `langgraph.json` independently exposes `./src/taxonomy_generator/graph.py:graph`. `main.py` remains a directly runnable entrypoint (`python main.py`). Prompt Markdown files are read from the installed package directory at import time by `prompts/__init__.py`, so package builds must include those files even though the explicit package-data rule mentions `py.typed`.

`utils.load_chat_model` requires a string containing `/`, splits once into `provider` and `model`, and delegates to LangChain `init_chat_model`; a missing slash raises `ValueError` during split and an unknown/provider-unavailable model fails in the dependency. Declared provider integrations include OpenAI, Anthropic, Fireworks, Groq, and Ollama through the corresponding LangChain packages. README installation claims (`pip install delve-taxonomy-generator` or requirements installation) are supporting usage documentation; the authoritative executable contract is the `pyproject.toml` console script and source layout. README model environment overrides are not implemented by `settings.py`; `.env` loading supplies provider environment values, not general YAML setting overrides.

## Internal boundary

Nodes in `taxonomy_generator.nodes`, routing functions, `schemas.py` classes, `utils` chain helpers, and prompt constants are implementation surfaces, not re-exported by `__init__.py`. They can be imported for focused integration work, but changing them is not a compatible public API change unless the package exports and documentation are updated. Public extension seams are supplying `documents`, `RunnableConfig.configurable` overrides, custom YAML, and provider/model names; adding a node requires graph composition changes.

## Validation

Use `python -c "import taxonomy_generator; print(taxonomy_generator.__all__)"`, `python -c "from taxonomy_generator.graph import graph; print(graph)"`, and `python -m build` (if the build dependency is installed) to check import, graph, and packaging surfaces without invoking an LLM. No automated tests are present.
