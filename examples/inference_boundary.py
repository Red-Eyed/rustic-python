"""Validate inference options once, then pass plain records to a numerical core."""

from typing import Annotated, NamedTuple, TypedDict

from pydantic import BaseModel, ConfigDict, Field, FiniteFloat


class InferenceConfig(BaseModel, frozen=True):
    """Validate external options outside the numerical execution path."""

    model_config = ConfigDict(strict=True, extra="forbid")
    temperature: Annotated[FiniteFloat, Field(gt=0)]


class InferenceParameters(NamedTuple):
    """Carry already-validated scalar options without a runtime validation layer."""

    temperature: float


class InferenceOutput(TypedDict):
    """Describe the plain dictionary returned by the numerical core."""

    scaled_logits: tuple[float, ...]


def prepare_inference(payload: str) -> InferenceParameters:
    """Parse JSON options or raise ValidationError, then create plain parameters."""
    config = InferenceConfig.model_validate_json(payload)
    return InferenceParameters(temperature=config.temperature)


def scale_logits(
    logits: tuple[float, ...], parameters: InferenceParameters
) -> InferenceOutput:
    """Scale scores using prepared options; perform no parsing or validation."""
    return {"scaled_logits": tuple(value / parameters.temperature for value in logits)}


parameters = prepare_inference('{"temperature": 2.0}')
output = scale_logits((2.0, -2.0), parameters)
# rejected[bad-typed-dict-key]: scores = output["probabilities"]
# rejected[bad-argument-type]: scale_logits((2.0,), InferenceConfig(temperature=2.0))
# rejected[bad-argument-type]: prepare_inference({})
