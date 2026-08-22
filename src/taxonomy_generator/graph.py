"""Define a custom Reasoning and Action agent.

Works with a chat model with tool calling support.
"""

from langgraph.graph import END, START, StateGraph

from taxonomy_generator.configuration import Configuration
from taxonomy_generator.nodes.corpus_loader import load_corpus
from taxonomy_generator.nodes.dimension_selector import select_dimensions
from taxonomy_generator.nodes.doc_labeler import label_documents
from taxonomy_generator.nodes.minibatches_generator import generate_minibatches
from taxonomy_generator.nodes.open_coder import open_code_minibatch
from taxonomy_generator.nodes.saturation_checker import check_saturation
from taxonomy_generator.nodes.summary_generator import generate_summaries
from taxonomy_generator.nodes.taxonomy_generator import generate_taxonomy
from taxonomy_generator.nodes.taxonomy_reviewer import review_taxonomy
from taxonomy_generator.nodes.taxonomy_updater import update_taxonomy
from taxonomy_generator.nodes.value_aggregator import aggregate_new_values
from taxonomy_generator.nodes.value_consolidator import consolidate_values
from taxonomy_generator.routing.should_aggregate_values import should_aggregate_values
from taxonomy_generator.routing.should_generate_or_update import (
    should_generate_or_update,
)
from taxonomy_generator.routing.should_review import should_review
from taxonomy_generator.routing.should_summarize import should_summarize
from taxonomy_generator.state import InputState, OutputState, State

builder = StateGraph(State, input_schema=InputState, output_schema=OutputState, context_schema=Configuration)

# Add nodes
builder.add_node("load_corpus", load_corpus)
builder.add_node("summarize", generate_summaries)
builder.add_node("get_minibatches", generate_minibatches)
builder.add_node("open_code_minibatch", open_code_minibatch)
builder.add_node("generate_taxonomy", generate_taxonomy)
builder.add_node("update_taxonomy", update_taxonomy)
builder.add_node("check_saturation", check_saturation)
builder.add_node("review_taxonomy", review_taxonomy)
builder.add_node("consolidate_values", consolidate_values)
builder.add_node("select_dimensions", select_dimensions)
builder.add_node("label_documents", label_documents)
builder.add_node("aggregate_new_values", aggregate_new_values)

# Add edges
builder.add_edge(START, "load_corpus")
builder.add_conditional_edges(
    "load_corpus",
    should_summarize,
    {
        "summarize": "summarize",
        "get_minibatches": "get_minibatches",
        # Test mode: classify directly against the seeded frozen taxonomy.
        "label_documents": "label_documents",
    }
)
builder.add_edge("summarize", "get_minibatches")
builder.add_edge("get_minibatches", "open_code_minibatch")

# The first open-coding pass (no taxonomy yet) feeds initial generation;
# every later pass feeds an incremental update.
builder.add_conditional_edges(
    "open_code_minibatch",
    should_generate_or_update,
    {
        "generate_taxonomy": "generate_taxonomy",
        "update_taxonomy": "update_taxonomy",
    }
)

# Both axial-coding steps flow into the saturation check, which also
# handles exhaustion (fewer remaining batches than the streak threshold,
# e.g. a single-minibatch corpus) by routing on to review.
builder.add_edge("generate_taxonomy", "check_saturation")
builder.add_edge("update_taxonomy", "check_saturation")

# After each axial pass: continue open-coding the next batch, or move on to
# review when saturated or when the minibatches are exhausted.
builder.add_conditional_edges(
    "check_saturation",
    should_review,
    {
        "open_code_minibatch": "open_code_minibatch",
        "review_taxonomy": "review_taxonomy",
    }
)

# Post-review stages: value consolidation, use-case dimension selection,
# then two-level labeling.
builder.add_edge("review_taxonomy", "consolidate_values")
builder.add_edge("consolidate_values", "select_dimensions")
builder.add_edge("select_dimensions", "label_documents")

# After labeling: train mode ends; test mode aggregates proposed new values
# into the frozen dimensions and emits the delta summary.
builder.add_conditional_edges(
    "label_documents",
    should_aggregate_values,
    {
        "aggregate_new_values": "aggregate_new_values",
        "__end__": END,
    }
)
builder.add_edge("aggregate_new_values", END)

graph = builder.compile()
graph.name = "Taxonomy Generation"