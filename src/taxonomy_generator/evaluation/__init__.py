"""Taxonomy evaluation suite (deepeval GEval-based, observe-only).

Scores a taxonomy view against the pipeline's existing quality criteria as
LLM-as-judge metrics, compares multiple saved taxonomies for run-to-run
consistency, and returns a plain scoreboard dict that the CLI, the saved
JSON artifacts, and the grounded-theory report section all render from.
"""

from taxonomy_generator.evaluation.judge import resolve_judge_model

__all__ = ["resolve_judge_model"]