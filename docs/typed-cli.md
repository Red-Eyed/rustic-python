# A typed CLI schema

[Project overview and reading path](../README.md)

A command accepts a positive worker count. Its application code should use a declared field, and CLI validation should share the same schema.

**Typical Python**

```python,ignore
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("--workers", type=int, default=4)
options = parser.parse_args()
workers = options.worker_count
```

The namespace does not declare the expected field for the checker. The typo fails at runtime, and `type=int` alone accepts a negative worker count.

**Alternative**

```python,ignore
from typing import Annotated
from pydantic import Field
from pydantic_settings import BaseSettings, CliApp


class Arguments(BaseSettings):
    workers: Annotated[int, Field(gt=0)] = 4


options = CliApp.run(Arguments, cli_args=["--workers", "4"])
workers = options.workers
```

The explicit argument list produces `workers == 4`. `options.worker_count` is
now a checker error. Invalid ranges are rejected by runtime parsing; typing does
not inspect arbitrary command-line text.

Keep command dispatch and output at the entry point. `CliSubCommand`,
`CliPositionalArg`, and `CliImplicitFlag` extend the same typed schema when needed.
The example shows the argument flow on the page; no terminal invocation is required.
