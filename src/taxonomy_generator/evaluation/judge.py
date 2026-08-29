"""Judge-model resolution for deepeval metrics.

Policy: use deepeval's built-in OpenAI integration directly whenever the
configured judge model is an OpenAI model (or OpenAI-compatible endpoint
via ``OPENAI_API_KEY`` / ``OPENAI_API_BASE``), because ``GEval`` accepts a
bare OpenAI model name and drives it through its own well-tested
integration.

Note on non-OpenAI providers: when the configured judge model targets a
provider deepeval does not support natively (e.g. ``groq/...``,
``fireworks/...``, or a local ``ollama/...`` endpoint that is not
OpenAI-compatible), do NOT pass the provider-qualified string to GEval —
it would be interpreted as an OpenAI model name and fail. The intended
future solution is a small ``DeepEvalBaseLLM`` adapter (e.g. a
``LangChainJudge`` class wrapping this repo's existing
``taxonomy_generator.utils.load_chat_model()``, implementing
``load_model``/``a_generate``/``generate``/``get_model_name``). That
wrapper is deliberately NOT implemented yet; until it exists,
non-OpenAI judge models raise a clear ``ValueError`` naming the provider.
"""

from __future__ import annotations

import logging
import os

logger = logging.getLogger(__name__)

# deepeval anonymous telemetry is always opted out for this project: set
# before any deepeval import has a chance to record an event.
os.environ.setdefault("DEEPEVAL_TELEMETRY_OPT_OUT", "1")

_SUPPORTED_PROVIDER = "openai"


def resolve_judge_model(model_name: str | None) -> str | None:
    """Resolve the configured judge model into a deepeval model argument.

    Args:
        model_name: The judge model in this pipeline's ``provider/model``
            format (from ``evaluation.judge_model`` or ``models.model``).

    Returns:
        The bare model name when the provider is OpenAI (deepeval's built-in
        integration consumes it directly), or ``None`` to let GEval use its
        own default OpenAI model when the input is ``None``/empty.

    Raises:
        ValueError: When a non-OpenAI provider is configured — see the
            module docstring for the future wrapper path.
    """
    if not model_name:
        # GEval's built-in default (OpenAI, OPENAI_API_KEY-driven).
        return None

    provider, _, model = model_name.partition("/")
    if provider != _SUPPORTED_PROVIDER:
        raise ValueError(
            f"Evaluation judge model '{model_name}' uses provider '{provider}', "
            "which deepeval's built-in integration does not support directly. "
            "Use an OpenAI model (or OpenAI-compatible endpoint), or wait for "
            "the planned DeepEvalBaseLLM wrapper over load_chat_model()."
        )

    logger.debug("Judge model resolved to deepeval built-in OpenAI model: %s", model)
    return model