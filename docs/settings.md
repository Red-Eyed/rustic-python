# Settings at startup

[Project overview and reading path](../README.md)

A service takes its worker count from the environment. Every component should use the same validated setting.

**Typical Python**

```text
import os

workers = int(os.environ.get("APP_WORKERS", "4"))
```

The conversion accepts negative counts and leaves the schema and defaults scattered across read sites.

**Alternative**

```text
from typing import Annotated
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="APP_")
    workers: Annotated[int, Field(gt=0)] = 4

settings = Settings()
workers = settings.workers
```

With `APP_WORKERS` set to `"4"`, the field is integer `4`. A negative value raises
`ValidationError` during startup. A misspelled `settings.worker_count` is rejected
by the checker. Parsing the text and checking its range still happen at runtime.

Load settings once at the entry point and pass values to components. Explicit
arguments override environment values; a dotenv file must be selected deliberately.
Malformed JSON for complex settings can raise `SettingsError` before validation.
A configuration editor supporting correction should return a typed failure instead
of treating invalid settings as an unrecoverable startup error.
