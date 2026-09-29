# Declared fields instead of reflection

[Project overview and reading path](../README.md)

A service reads a retry limit from a known configuration. Renaming or misspelling a field should be caught during development.

**Typical Python**

```text
retries = getattr(config, "retrise", 3)
```

The typo silently selects the fallback. Attribute names passed as strings hide the intended field contract.

**Alternative**

```text
from dataclasses import dataclass

@dataclass(frozen=True)
class Config:
    retries: int = 3

config = Config()
retries = config.retries
```

Direct `config.retrise` is rejected as `missing-attribute`; the valid access
returns `3`. The default belongs in the model, where all callers share its policy.

Keep `getattr`, `setattr`, `hasattr`, `delattr`, and equivalent reflection out of
ordinary application logic. Use a protocol for required capabilities and a typed
registry for selecting handlers. `hasattr` does not establish a method signature.
Necessary framework adapters and tests may use reflection locally, then return
precise types. This is a design policy, not a claim that checkers reject all reflection.
