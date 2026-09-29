# Settings at startup

[Project overview and reading path](../README.md)

A service takes its worker count from the environment. Every component should use the same validated setting.

**Typical Python**

```python,ignore
import os

workers = int(os.environ.get("APP_WORKERS", "4"))
```

The conversion accepts negative counts and leaves the schema and defaults scattered across read sites.

**Alternative**

```python,ignore
from dataclasses import dataclass
from typing import Annotated, TypeAlias, assert_never

from pydantic import Field, ValidationError
from pydantic_settings import BaseSettings, SettingsConfigDict, SettingsError


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="APP_")
    workers: Annotated[int, Field(gt=0)] = 4


@dataclass(frozen=True)
class InvalidSettings:
    reason: str


SettingsResult: TypeAlias = Settings | InvalidSettings


def load_settings() -> SettingsResult:
    try:
        return Settings()
    except (ValidationError, SettingsError) as error:
        return InvalidSettings(str(error))


outcome = load_settings()
match outcome:
    case Settings(workers=workers):
        pass
    case InvalidSettings(reason=reason):
        pass
    case _:
        assert_never(outcome)
```

With `APP_WORKERS` set to `"4"`, matching the success variant binds integer
`workers == 4`. A negative or malformed value returns `InvalidSettings`.
The checker rejects using `.workers` on the unhandled `SettingsResult`, or a
misspelled field on `Settings`. Parsing and range checks still happen at runtime.

Load settings once at the entry point and pass values to components. Explicit
arguments override environment values; a dotenv file must be selected deliberately.
`SettingsError` from malformed complex settings is also translated at this
boundary. Unexpected defects still surface as exceptions.
