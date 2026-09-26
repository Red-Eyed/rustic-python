"""Check the runtime obligations that complement the guide's static contracts."""

import json
from math import isfinite

import pytest
from pydantic import JsonValue, ValidationError

from examples.explicit_results import Err, InvalidLabel, Ok, parse_label
from examples.generic_batches import Batch, first
from examples.immutable_config import Experiment
from examples.preprocessing_state import UnfittedCenterer
from examples.reasoned_absence import Absent, precision
from examples.semantic_types import Logits, softmax
from examples.task_variants import Classification, Regression
from examples.validated_records import parse_metadata


def test_softmax_handles_large_scores() -> None:
    """Large finite logits should normalize without exponential overflow."""
    result = softmax(Logits((1000.0, 1001.0, 999.0)))
    assert all(isfinite(value) and 0 <= value <= 1 for value in result)
    assert sum(result) == pytest.approx(1.0)
    assert result[1] > result[0] > result[2]


@pytest.mark.parametrize("scores", [(), (float("nan"),), (float("inf"),)])
def test_softmax_rejects_invalid_scores(scores: tuple[float, ...]) -> None:
    """Runtime validation rejects values that container types cannot exclude."""
    with pytest.raises(ValueError):
        softmax(Logits(scores))


@pytest.mark.parametrize("raw", ["cat", "-1", "", "7.5"])
def test_bad_label_preserves_input(raw: str) -> None:
    """A rejected label retains both the input and its explanation."""
    outcome = parse_label(raw)
    match outcome:
        case Err(error=InvalidLabel(raw=original, reason=reason)):
            assert original == raw
            assert reason
        case _:
            pytest.fail("expected an explicit label error")


@pytest.mark.parametrize(("raw", "expected"), [("0", 0), ("7.0", 7)])
def test_numeric_label_text_is_valid(raw: str, expected: int) -> None:
    """Accept zero and integer-valued decimal text under the parsing policy."""
    assert parse_label(raw) == Ok(expected)


def test_undefined_precision_differs_from_zero() -> None:
    """An empty denominator and incorrect positive predictions remain distinct."""
    assert precision(0, 0) == Absent("no predicted positives")
    assert precision(0, 12) == 0.0


@pytest.mark.parametrize(
    "payload",
    [
        None,
        [],
        {},
        {"name": "data", "num_classes": True},
        {"name": "", "num_classes": 10},
        {"name": "data", "num_classes": 1},
    ],
)
def test_metadata_rejects_invalid_payload(payload: JsonValue) -> None:
    """Reject malformed external data, including booleans masquerading as counts."""
    with pytest.raises(ValueError):
        parse_metadata(json.dumps(payload))


def test_metadata_discards_extra_fields() -> None:
    """The parser's documented extra-field policy keeps only the canonical schema."""
    assert parse_metadata(
        json.dumps({"name": "data", "num_classes": 3, "extra": 1})
    ) == {
        "name": "data",
        "num_classes": 3,
    }


def test_centerer_uses_training_mean() -> None:
    """Fitting establishes the offset subsequently used for transformation."""
    fitted = UnfittedCenterer().fit((2.0, 4.0, 6.0))
    assert fitted.transform(5.0) == pytest.approx(1.0)


def test_empty_batch_is_rejected() -> None:
    """A well-typed empty batch still requires runtime handling."""
    batch: Batch[int] = Batch(())
    with pytest.raises(ValueError):
        first(batch)


@pytest.mark.parametrize("count", [-1, 0, 1])
def test_invalid_task_parameters_are_rejected(count: int) -> None:
    """Numerical constraints remain enforced at construction, beyond static types."""
    with pytest.raises(ValueError):
        Classification(num_classes=count)
    with pytest.raises(ValueError):
        Regression(huber_delta=float("nan"))


@pytest.mark.parametrize("attribute", ["seed", "features"])
def test_frozen_config_rejects_dynamic_assignment(attribute: str) -> None:
    """Ordinary runtime attribute assignment respects frozen settings models."""
    config = Experiment(seed=17, features=("height",))
    with pytest.raises(ValidationError, match="frozen"):
        setattr(config, attribute, 23)
