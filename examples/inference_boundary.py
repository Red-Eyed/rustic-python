"""Validate inference settings before handing plain parameters to model code."""

from typing import Annotated, NamedTuple

from pydantic import BaseModel, ConfigDict, Field, FiniteFloat


class InferenceConfig(BaseModel, frozen=True):
    """Validate external options outside the numerical execution path."""

    model_config = ConfigDict(strict=True, extra="forbid")
    temperature: Annotated[FiniteFloat, Field(gt=0)]


class InferenceParameters(NamedTuple):
    """Carry already-validated scalar options without a runtime validation layer."""

    temperature: float


def prepare_inference(payload: str) -> InferenceParameters:
    """Parse startup options; invalid configuration aborts with ValidationError."""
    config = InferenceConfig.model_validate_json(payload)
    return InferenceParameters(temperature=config.temperature)


parameters = prepare_inference('{"temperature": 2.0}')
temperature: float = parameters.temperature
# rejected[missing-attribute]: temperature = parameters.temprature
# rejected[bad-assignment]: wrong: InferenceParameters = InferenceConfig(temperature=2.0)
# rejected[bad-argument-type]: prepare_inference({})
