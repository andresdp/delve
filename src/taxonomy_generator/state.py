"""Define the state structures for the agent."""

from __future__ import annotations

import operator
from dataclasses import dataclass, field
from typing import Annotated, Dict, List, Literal, Optional, Sequence

from langchain_core.messages import AnyMessage
from langgraph.graph import add_messages
from langgraph.managed import IsLastStep
from pydantic import BaseModel


@dataclass
class Doc:
    """Represents a document in the taxonomy generation process."""
    id: str
    content: str
    summary: Optional[str] = None
    explanation: Optional[str] = None
    category: Optional[str] = None
    value: Optional[str] = None
    score: Optional[float] = None

    def __str__(self) -> str:
        """Return a clean content preview instead of the full repr."""
        preview = self.content[:100].replace("\n", " ").strip()
        if len(self.content) > 100:
            preview += "..."
        return preview


class UserFeedback(BaseModel):
    """Represents feedback on the taxonomy.

    The producer may be a human (pre-populated state or human-in-the-loop)
    or an automated critic (e.g., the saturation checker reporting uncovered
    concepts) — both flow into the same ``{feedback}`` prompt slot.

    Attributes:
        decision: Whether to continue with current taxonomy or modify it
        explanation: Explanation of why this decision was made
        feedback: Optional specific feedback from the producer
    """
    decision: Literal["continue", "modify"]
    explanation: str
    feedback: Optional[str] = None


@dataclass
class InputState:
    """Defines the input state for the agent, representing initial configuration parameters.

    Pass a list of documents (as Doc objects or dicts with 'id' and 'content' keys)
    via the `documents` field. Use ``strings_to_docs()`` to convert raw strings.
    Optionally pass ``external_feedback`` to inject external feedback (e.g. from
    the CLI ``--feedback`` flag or the ``feedback`` config section) into
    taxonomy refinement prompts. This channel is persistent for the whole run —
    unlike ``state.user_feedback``, which the automated saturation critic owns
    and overwrites.
    """
    documents: List[Doc] = field(default_factory=list)
    external_feedback: Optional[UserFeedback] = field(default=None)


@dataclass
class OutputState:
    """Defines the output state for the agent, representing the interaction history."""
    messages: Annotated[Sequence[AnyMessage], add_messages] = field(default_factory=list)
    clusters: Annotated[List[List[Dict]], operator.add] = field(default_factory=list)
    explanations: Annotated[List[str], operator.add] = field(default_factory=list)
    documents: List[Doc] = field(default_factory=list)
    selected_clusters: List[List[Dict]] = field(default_factory=list)
    dropped_dimensions: List[Dict] = field(default_factory=list)
    delta_summary: Optional[Dict] = field(default=None)
    # Observe-only evaluation scoreboard (deepeval GEval criteria). Flat
    # dict with replace semantics — always ends the run holding the final
    # (post-selection/post-labeling) evaluate_taxonomy call's scoreboard,
    # since that call always executes last.
    evaluation: Optional[Dict] = field(default=None)
    # Every evaluate_taxonomy call (mid-loop drafts and the final call),
    # in execution order — unlike `evaluation`, this accumulates rather
    # than replacing, so format_feedback can read the freshest entry at
    # any point in the run, not just the final one.
    evaluation_history: Annotated[List[Dict], operator.add] = field(default_factory=list)


@dataclass
class State(InputState, OutputState):
    """Represents the complete state of the taxonomy generation agent.
    
    This class extends InputState and OutputState with additional attributes needed 
    throughout the taxonomy generation process.
    """
    documents: List[Doc] = field(default_factory=list)
    minibatches: List[List[int]] = field(default_factory=list)
    clusters: Annotated[List[List[Dict]], operator.add] = field(default_factory=list)
    explanations: Annotated[List[str], operator.add] = field(default_factory=list)
    status: Annotated[List[str], operator.add] = field(default_factory=list)
    # Open codes accumulate across minibatches, mirroring `clusters`.
    open_codes: Annotated[List[Dict], operator.add] = field(default_factory=list)
    # Index of the next minibatch to open-code (advances ahead of axial coding).
    open_code_batch_index: int = field(default=0)
    # Theoretical-saturation tracking (per-minibatch verdicts + current streak).
    saturation_history: Annotated[List[Dict], operator.add] = field(default_factory=list)
    saturation_streak: int = field(default=0)
    # Use-case-selected subset of the final reviewed taxonomy. Kept distinct from
    # the full `clusters[-1]` so both full and filtered taxonomies stay inspectable.
    selected_clusters: List[List[Dict]] = field(default_factory=list)
    # Dimensions dimension-selection excluded from selected_clusters, kept
    # inspectable with a rationale rather than only logged to `status`.
    dropped_dimensions: List[Dict] = field(default_factory=list)
    use_case: str = field(default="")
    is_last_step: IsLastStep = field(default=False)
    user_feedback: UserFeedback = field(default=None)

