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
        default="",
        description="Brief reasoning for the clustering decisions.",
    )


class LabelOutput(BaseModel):
    """Structured output for document labeling."""

    reasoning: str = Field(
        description="Chain of reasoning for why the category was selected."
    )
    category: str = Field(
        description="The single most relevant category name from the taxonomy."
    )