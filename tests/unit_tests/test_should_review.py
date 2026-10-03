"""Routing after the saturation check: saturation ends the loop only after a minimum share of the corpus."""

from taxonomy_generator.routing.should_review import coded_fraction, should_review
from taxonomy_generator.state import State

TEN_BATCHES = [[i * 10 + j for j in range(10)] for i in range(10)]


def _config(min_fraction=0.7, streak=3):
    return {"configurable": {"saturation_streak_threshold": streak,
                             "saturation_min_corpus_fraction": min_fraction}}


def _state(batches_coded, streak):
    return State(minibatches=TEN_BATCHES, open_code_batch_index=batches_coded,
                 clusters=[[]] * batches_coded, saturation_streak=streak)


def test_coded_fraction_counts_documents_of_coded_batches():
    state = State(minibatches=[[0, 1, 2], [3, 4, 5], [6]], open_code_batch_index=2)
    assert coded_fraction(state) == 6 / 7


def test_saturation_before_the_minimum_share_keeps_coding():
    assert should_review(_state(4, streak=3), _config()) == "open_code_minibatch"


def test_saturation_after_the_minimum_share_moves_to_review():
    assert should_review(_state(7, streak=3), _config()) == "review_taxonomy"


def test_minimum_share_without_saturation_keeps_coding():
    assert should_review(_state(8, streak=1), _config()) == "open_code_minibatch"


def test_zero_minimum_lets_saturation_alone_decide():
    assert should_review(_state(4, streak=3), _config(min_fraction=0.0)) == "review_taxonomy"


def test_exhausted_minibatches_always_move_to_review():
    assert should_review(_state(10, streak=0), _config()) == "review_taxonomy"
