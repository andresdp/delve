"""Define the configurable parameters for the agent."""

from __future__ import annotations

import os
from dataclasses import dataclass, field, fields
from typing import Annotated, Optional

from langchain_core.runnables import RunnableConfig, ensure_config

_DEFAULT_MODEL = "openai/gpt-5.4-nano"
_DEFAULT_FAST_LLM = "openai/gpt-5.4-nano"


@dataclass(kw_only=True)
class Configuration:
    """The configuration for the agent."""

    model: Annotated[str, {"__template_metadata__": {"kind": "llm"}}] = field(
        default_factory=lambda: os.environ.get("LLM_MODEL", _DEFAULT_MODEL),
        metadata={
            "description": "The name of the language model to use for the agent's main interactions. "
            "Should be in the form: provider/model-name. "
            "Can be set via the LLM_MODEL environment variable. "
            "Defaults to openai/gpt-5.4-nano."
        },
    )

    fast_llm: Annotated[str, {"__template_metadata__": {"kind": "llm"}}] = field(
        default_factory=lambda: os.environ.get("LLM_FAST_MODEL", _DEFAULT_FAST_LLM),
        metadata={
            "description": "A faster, lighter model for tasks like summarization. "
            "Should be in the form: provider/model-name. "
            "Can be set via the LLM_FAST_MODEL environment variable. "
            "Defaults to openai/gpt-5.4-nano."
        },
    )

    max_runs: int = field(
        default=500,
        metadata={
            "description": "Maximum number of runs to retrieve from LangSmith. "
            "Only used in LangSmith retrieval mode."
        },
    )

    sample_size: int = field(
        default=50,
        metadata={
            "description": "Number of runs to sample for processing. "
            "Only used in LangSmith retrieval mode. When providing documents directly, "
            "all documents are used."
        },
    )

    batch_size: int = field(
        default=200,
        metadata={
            "description": "Size of minibatches for document processing."
        },
    )

    suggestion_length: int = field(
        default=30,
        metadata={"description": "Maximum length for taxonomy suggestions"}
    )
    cluster_name_length: int = field(
        default=10,
        metadata={"description": "Maximum length for cluster names"}
    )
    cluster_description_length: int = field(
        default=30,
        metadata={"description": "Maximum length for cluster descriptions"}
    )
    explanation_length: int = field(
        default=20,
        metadata={"description": "Maximum length for explanations"}
    )
    max_num_clusters: int = field(
        default=25,
        metadata={"description": "Maximum number of clusters allowed"}
    )

    @classmethod
    def from_runnable_config(
        cls, config: Optional[RunnableConfig] = None
    ) -> Configuration:
        """Create a Configuration instance from a RunnableConfig object."""
        config = ensure_config(config)
        configurable = config.get("configurable") or {}
        _fields = {f.name for f in fields(cls) if f.init}
        return cls(**{k: v for k, v in configurable.items() if k in _fields})
