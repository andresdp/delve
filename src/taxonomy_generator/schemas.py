"""Pydantic schemas for structured LLM outputs."""

from __future__ import annotations

from typing import List, Literal, Optional

from pydantic import BaseModel, Field


class SummaryOutput(BaseModel):
    """Structured output for document summarization."""

    summary: str = Field(description="A concise summary of the text.")
    explanation: str = Field(description="A brief explanation of the key points or themes.")


class OpenCode(BaseModel):
    """A fine-grained per-document concept or decision label (open coding)."""

    doc_id: str = Field(description="Id of the document the code was extracted from.")
    label: str = Field(description="Concise open-code label naming the concept or decision found in the document.")
    rationale: str = Field(description="Why this code applies to the document, grounded in the use case.")


class OpenCodesOutput(BaseModel):
    """Structured output for the open-coding step of one document."""

    codes: List[OpenCode] = Field(
        description="Open codes extracted from the document. Empty list when none apply."
    )


class Relation(BaseModel):
    """A typed link between two dimensions (grounded theory paradigm model)."""

    target_id: str = Field(description="Id of the dimension this relation points to.")
    type: Literal["precondition", "consequence", "co_occurring", "constrains"] = Field(
        description=(
            "precondition: choosing a value on the target dimension is required before "
            "this dimension applies. consequence: choices on this dimension imply outcomes "
            "on the target dimension. co_occurring: values on both dimensions appear "
            "together more than chance but neither causes the other. constrains: values on "
            "this dimension restrict the available values on the target dimension."
        )
    )
    rationale: str = Field(
        description="Why this relation holds, judged against the use case — not incidental textual co-occurrence."
    )


class Value(BaseModel):
    """A consolidated decision/value within one dimension — a point on the axis."""

    id: str = Field(description="Value identifier, unique within its dimension (e.g., '1.1').")
    dimension_id: str = Field(description="Id of the dimension this value belongs to.")
    label: str = Field(description="Concise value label naming the specific decision or position.")
    description: str = Field(description="What this value means along its dimension.")
    supporting_doc_ids: List[str] = Field(
        default_factory=list,
        description="Ids of documents whose open codes support this value.",
    )


class Cluster(BaseModel):
    """A single taxonomy category (dimension)."""

    id: str = Field(description="Category number, starting from 1, incremented.")
    name: str = Field(description="Concise category name as a noun-driven phrase (e.g., 'Request Routing Strategy', not 'Route Requests').")
    description: str = Field(
        description="Category description that differentiates it from others."
    )
    relations: List[Relation] = Field(
        default_factory=list,
        description="Typed relations from this dimension to other dimensions, judged against the use case.",
    )
    values: List[Value] = Field(
        default_factory=list,
        description="Draft values (decisions) along this dimension that the data supports.",
    )


class TaxonomyOutput(BaseModel):
    """Structured output for taxonomy generation, update, and review."""

    clusters: List[Cluster] = Field(
        description="List of taxonomy categories."
    )
    explanation: str = Field(
        description=(
            "Your rationale for this taxonomy: why you chose these categories, "
            "how they capture the themes in the data, and what trade-offs you made. "
            "Must not be empty."
        ),
    )


class SaturationCheckOutput(BaseModel):
    """Per-minibatch verdict on theoretical saturation."""

    is_saturated: bool = Field(
        description="True when every open code in the minibatch is subsumed by an existing dimension."
    )
    uncovered_concepts: List[str] = Field(
        default_factory=list,
        description="Open-code concepts not captured by any existing dimension. Empty when saturated.",
    )
    rationale: str = Field(
        description="Why this verdict holds, relative to the design space's goals (the use case)."
    )


class DroppedDimension(BaseModel):
    """A dimension dropped by selection, kept inspectable with its rationale."""

    id: str = Field(description="Id of the dropped dimension.")
    rationale: str = Field(description="Why this dimension was deemed irrelevant to the use case.")


class SelectionOutput(BaseModel):
    """Structured output for selective coding (use-case relevance filtering)."""

    selected_ids: List[str] = Field(
        description="Ids of the dimensions relevant to the use case, in order of relevance."
    )
    dropped: List[DroppedDimension] = Field(
        default_factory=list,
        description="Dimensions dropped from the final taxonomy, each with a rationale. Kept inspectable, never silently deleted."
    )
    rationale: str = Field(
        description="Overall reasoning for the selected subset."
    )


class ValueMergeOutput(BaseModel):
    """LLM adjudication for one borderline value-merge pair."""

    same_decision: bool = Field(
        description="True when both values name the same decision within the dimension."
    )
    rationale: str = Field(description="Why the two values are or are not the same decision, judged against the use case.")


class LabelOutput(BaseModel):
    """Structured output for document labeling."""

    reasoning: str = Field(
        description="Chain of reasoning for why the category was selected."
    )
    category: str = Field(
        description="The single most relevant category name from the taxonomy."
    )
    score: float = Field(
        description=(
            "Confidence score between 0.0 and 1.0 indicating how well the document "
            "fits the chosen category. 1.0 = perfect fit, 0.5 = ambiguous or partial "
            "match, close to 0.0 = poor fit (likely fallback)."
        ),
    )
    value_id: Optional[str] = Field(
        default=None,
        description=(
            "Id of the specific value (decision) within the chosen category that best "
            "matches the document. Null when the category has no values or none fit."
        ),
    )