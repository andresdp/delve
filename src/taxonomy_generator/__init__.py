"""Taxonomy Generator.

This module defines a custom taxonomy generation agent graph.
It processes documents and generates taxonomies.

Pass a list of documents via the ``documents`` field.
Use ``strings_to_docs()`` to convert raw strings, or pass dicts/Doc objects directly.
"""

from taxonomy_generator.configuration import Configuration, init_settings
from taxonomy_generator.graph import graph
from taxonomy_generator.settings import Settings
from taxonomy_generator.state import Doc, InputState, OutputState, State, UserFeedback
from taxonomy_generator.utils import docs_from_dicts, strings_to_docs

__all__ = [
    "graph",
    "Configuration",
    "Settings",
    "init_settings",
    "State",
    "InputState",
    "OutputState",
    "Doc",
    "UserFeedback",
    "strings_to_docs",
    "docs_from_dicts",
]
