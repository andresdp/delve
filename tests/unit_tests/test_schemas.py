"""Tests for the decision-status field on OpenCode and Value (Plan U1)."""

import pytest
from pydantic import ValidationError

from taxonomy_generator.schemas import OpenCode, Value


def test_open_code_without_status_raises_validation_error():
    with pytest.raises(ValidationError):
        OpenCode(doc_id="d1", label="Uses caching", rationale="Doc describes a caching decision.")


def test_value_without_status_defaults_to_accepted():
    value = Value(
        id="1.1",
        dimension_id="1",
        label="Client-side caching",
        description="Caching happens on the client.",
    )
    assert value.status == "accepted"


def test_open_code_with_bogus_status_raises_validation_error():
    with pytest.raises(ValidationError):
        OpenCode(
            doc_id="d1",
            label="Uses caching",
            rationale="Doc describes a caching decision.",
            status="bogus",
        )


def test_value_with_bogus_status_raises_validation_error():
    with pytest.raises(ValidationError):
        Value(
            id="1.1",
            dimension_id="1",
            label="Client-side caching",
            description="Caching happens on the client.",
            status="bogus",
        )
