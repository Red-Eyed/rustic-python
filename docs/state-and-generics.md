# State, generics, and immutability

[Project overview and reading path](../README.md)

## Encode preprocessing state in the type

**Mistake:** a scaler exposes `transform` before it has statistics, using
`mean: float | None` and a runtime "not fitted" exception.

Return a different type after fitting. Here a one-dimensional mean-centering
transform makes the state transition explicit.

[Source](../examples/preprocessing_state.py)

```python
"""Expose transformation only after fitting a scalar centering model."""

from dataclasses import dataclass
from math import isfinite
from statistics import mean


@dataclass(frozen=True, slots=True)
class FittedCenterer:
    """Hold the fitted offset for a scalar feature."""

    offset: float

    def transform(self, value: float) -> float:
        """Center a finite scalar; reject nonfinite input."""
        if not isfinite(value):
            raise ValueError("value must be finite")
        return value - self.offset


@dataclass(frozen=True, slots=True)
class UnfittedCenterer:
    """Provide fitting without exposing transformation."""

    def fit(self, training_values: tuple[float, ...]) -> FittedCenterer:
        """Fit finite, nonempty training values; otherwise raise ValueError."""
        if not training_values or not all(isfinite(x) for x in training_values):
            raise ValueError("training values must be nonempty and finite")
        return FittedCenterer(offset=mean(training_values))


unfitted = UnfittedCenterer()
fitted = unfitted.fit((2.0, 4.0, 6.0))
centered = fitted.transform(5.0)
# rejected[missing-attribute]: unfitted.transform(5.0)
```

**Static guarantee:** `UnfittedCenterer` has no transformation operation. Callers
working through this API must obtain a fitted value first.

**Runtime obligation:** this is not Rust move semantics. The old unfitted object
remains usable, and the public `FittedCenterer` constructor can be called directly.
The pattern communicates permitted operations; it is not an unforgeable certificate
of training provenance. Validation-only fitting is still leakage even if it type-checks.

## Preserve relationships with generics

**Mistake:** a helper accepts and returns `object`, erasing what kind of sample it
contains. Callers then cast the result back to the type they hoped to receive.

Use a type parameter when an output's type depends on an input's type.

[Source](../examples/generic_batches.py)

```python
"""Preserve the sample type through a batch selection helper."""

from dataclasses import dataclass
from typing import Generic, TypeVar

T = TypeVar("T")


@dataclass(frozen=True, slots=True)
class Batch(Generic[T]):
    """Group samples of one statically known type."""

    samples: tuple[T, ...]


@dataclass(frozen=True, slots=True)
class LabeledSample:
    """Pair a feature vector with its class index."""

    features: tuple[float, ...]
    label: int


def first(batch: Batch[T]) -> T:
    """Return the first sample, or raise ValueError for an empty batch."""
    if not batch.samples:
        raise ValueError("batch must be nonempty")
    return batch.samples[0]


batch = Batch((LabeledSample((0.2, 0.8), label=1),))
sample: LabeledSample = first(batch)
# rejected[bad-assignment]: label: int = first(batch)
```

**Static guarantee:** `first(Batch[LabeledSample])` returns a `LabeledSample`.
The relationship survives without a cast. Reusing a type parameter is meaningful
when it relates inputs, outputs, or fields; it is not decoration.

**Runtime obligation:** `tuple[T, ...]` can be empty. If nonemptiness is central to
an API, model a required first element and a remaining tuple rather than repeatedly
checking it. A generic type also does not prove that every feature vector has the
same length. Python generics do not imply Rust-style monomorphization or a speedup.

## Be precise about immutability

**Mistake:** a supposedly frozen experiment config holds a mutable list, and a later
augmentation step changes it through an alias.

[Source](../examples/immutable_config.py)

```python
"""Keep a small experiment configuration immutable at each stored level."""

from typing import Annotated, Final

from pydantic import Field, StringConstraints, TypeAdapter, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Experiment(BaseSettings, frozen=True):
    """Record a seed and an immutable sequence of feature names."""

    model_config = SettingsConfigDict(env_prefix="RUSTIC_EXPERIMENT_", extra="forbid")
    seed: Annotated[int, Field(ge=0)] = 17
    features: Annotated[
        tuple[Annotated[str, StringConstraints(pattern=r"\S")], ...],
        Field(min_length=1),
    ] = ("height", "width")

    @field_validator("seed", mode="before")
    @classmethod
    def _parse_seed(cls, value: object) -> int:
        """Keep bool distinct from counts while allowing numeric settings text."""
        # A before-validator receives arbitrary library input; recover int here.
        match value:
            case bool():
                raise ValueError("seed must not be a boolean")
        return TypeAdapter(int).validate_python(value)


config = Experiment(seed=17, features=("height", "width"))
DEFAULT_SEED: Final[int] = 17
# rejected[read-only]: config.seed = 23
# rejected[missing-attribute]: config.features.append("area")
# rejected[bad-assignment]: DEFAULT_SEED = 23
```

**Static guarantee:** field reassignment, the nonexistent tuple mutation operation,
and rebinding a `Final` name are rejected.

**Runtime obligation:** frozen Pydantic models and dataclasses are shallow. A frozen record containing
a tensor still allows in-place tensor operations; a tuple can contain mutable
objects. `Final` prevents checked rebinding, not mutation of the referenced object.
Read-only interfaces such as `Sequence` limit what a consumer may do through that
interface but cannot prevent another alias from changing the underlying object.
None of these mechanisms establishes exclusive ownership or freedom from data races.

## Load settings at startup

Use `pydantic-settings` for environment and dotenv configuration. In the example,
`Experiment()` reads `RUSTIC_EXPERIMENT_SEED` and `RUSTIC_EXPERIMENT_FEATURES`.
Explicit arguments override environment values, which override an explicitly
selected dotenv file (`Experiment(_env_file=path)`), then defaults apply. The
example does not implicitly search for a dotenv file.

Settings arrive as text: a seed of `"23"` becomes `23`, and a JSON array of feature
names becomes a tuple. This intentional conversion differs from the strict SDK
payload policy. The seed validator excludes Python booleans; negative seeds,
invalid numeric text, empty feature collections, and blank names are invalid.
Do not assume blanket `strict=True` has identical behavior across settings sources
and direct model construction. Test the actual source path.

The seed before-validator is a Pydantic integration seam: the library can supply
arbitrary input before field validation. Its `object` parameter is localized to
that callback, which rejects booleans and returns a parsed `int`. Application
code consumes `Experiment.seed` as `int`; it never receives the unknown value.

Schema failures raise `ValidationError`; malformed JSON in a complex environment
value can raise `pydantic_settings.SettingsError` before model validation. Startup
code should report either as a configuration failure. The
[settings tests](../tests/test_validation.py) isolate the environment with a
fixture and cover source precedence and invalid values.

Load settings once at the application entry point and pass selected values to
components. Reading the environment inside a transform makes behavior depend on
hidden process state. Keep settings objects and validation outside compiled
inference. See [settings management](https://docs.pydantic.dev/latest/concepts/pydantic_settings/).

## Build CLIs with pydantic-settings

Use **pydantic-settings instead of hand-written argparse** for application CLIs.
Define arguments as typed model fields and run the command through `CliApp.run`.
Use `BaseSettings` when command options also come from environment configuration.
The CLI and environment then share field constraints rather than maintaining
separate validation rules.

Use `CliPositionalArg` for positional inputs, `CliImplicitFlag[bool]` for switches,
and `CliSubCommand` for commands such as training and evaluation. A command's
`cli_cmd` method should delegate to application functions; parsing, terminal
output, and process exit belong at the entry point.
See [pydantic-settings CLI support](https://docs.pydantic.dev/latest/concepts/pydantic_settings/#command-line-support).

Test explicit argument lists instead of letting tests consume pytest's arguments.
Cover invalid values, unknown options, help, and CLI/environment precedence.
For data tools, provide JSON output alongside human-readable output. Long-running
commands should display progress, with a quiet option; keep progress off stdout
when stdout carries machine-readable data.
