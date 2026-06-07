"""Pydantic schemas for structured LLM outputs."""

from __future__ import annotations

from pydantic import BaseModel, Field


class SummaryOutput(BaseModel):
    """Structured output for document summarization."""

    summary: str = Field(description="A concise summary of the text.")
    explanation: str = Field(description="A brief explanation of the key points or themes.")


class Cluster(BaseModel):
    """A single taxonomy category."""

    id: str = Field(description="Category number, starting from 1, incremented.")
    name: str = Field(description="Concise category name (verb or noun phrase).")
    description: str = Field(
        description="Category description that differentiates it from others."
    )


class TaxonomyOutput(BaseModel):
    """Structured output for taxonomy generation, update, and review."""

    clusters: list[Cluster] = Field(
        description="List of taxonomy categories."
    )
    explanation: str = Field(
        description=(
            "Your rationale for this taxonomy: why you chose these categories, "
            "how they capture the themes in the data, and what trade-offs you made. "
            "Must not be empty."
        ),
    )


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
