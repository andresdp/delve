"""Define the state structures for the agent."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Annotated, List, Optional, Dict, Sequence, Literal
import operator

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
    score: Optional[float] = None

    def __str__(self) -> str:
        """Return a clean content preview instead of the full repr."""
        preview = self.content[:100].replace("\n", " ").strip()
        if len(self.content) > 100:
            preview += "..."
        return preview


class UserFeedback(BaseModel):
    """Represents user feedback on the taxonomy.
    
    Attributes:
        decision: Whether to continue with current taxonomy or modify it
        explanation: Explanation of why this decision was made
        feedback: Optional specific feedback from the user
    """
    decision: Literal["continue", "modify"]
    explanation: str
    feedback: Optional[str] = None


@dataclass
class InputState:
    """Defines the input state for the agent, representing initial configuration parameters.
    
    Pass a list of documents (as Doc objects or dicts with 'id' and 'content' keys)
    via the `documents` field. Use ``strings_to_docs()`` to convert raw strings.
    """
    documents: List[Doc] = field(default_factory=list)


@dataclass
class OutputState:
    """Defines the output state for the agent, representing the interaction history."""
    messages: Annotated[Sequence[AnyMessage], add_messages] = field(default_factory=list)
    clusters: Annotated[List[List[Dict]], operator.add] = field(default_factory=list)
    explanations: Annotated[List[str], operator.add] = field(default_factory=list)
    documents: List[Doc] = field(default_factory=list)


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
    use_case: str = field(default="")
    is_last_step: IsLastStep = field(default=False)
    user_feedback: UserFeedback = field(default=None)

