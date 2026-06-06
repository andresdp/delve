"""Taxonomy Generator.

This module defines a custom taxonomy generation agent graph.
It processes documents and generates taxonomies.

Supports two input modes:
1. **Direct corpus input**: Pass a list of documents via the ``documents`` field.
   Use ``strings_to_docs()`` to convert raw strings, or pass dicts/Doc objects directly.
2. **LangSmith retrieval**: Provide ``project_name``, ``org_id``, and ``days`` to
   fetch conversation runs from LangSmith.
"""

from taxonomy_generator.graph import graph
from taxonomy_generator.configuration import Configuration
from taxonomy_generator.state import State, InputState, OutputState, Doc, UserFeedback
from taxonomy_generator.utils import strings_to_docs, docs_from_dicts

__all__ = [
    "graph", 
    "Configuration", 
    "State", 
    "InputState", 
    "OutputState",
    "Doc",
    "UserFeedback",
    "strings_to_docs",
    "docs_from_dicts",
]
