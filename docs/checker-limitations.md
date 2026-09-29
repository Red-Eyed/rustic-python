# Working with checker limitations

[Project overview and reading path](../README.md)

The manual narrowing examples here isolate checker behavior. For production
external schemas, use [Pydantic boundary validation](data-modeling.md), rather
than copying a checker reproduction into an application parser.

Python is not Rust, and a type checker is not an oracle. It can reject valid code,
lose information across an abstraction, trust an inaccurate stub, or accept a
program that fails at runtime. The objective is a useful checked codebase, not
rewriting every reasonable Python idiom until a tool stops complaining.

Keep workarounds local, explain the assumption they rely on, and retain a test that
can tell you when the workaround is no longer needed. Do not change the application's
meaning simply to fit an inference limitation.

## Diagnose before choosing a workaround

| Situation | What to establish | Smallest reasonable response |
| --- | --- | --- |
| Actual contract mismatch | Is the caller really supplying the wrong value or missing a case? | Fix the code or its declared API |
| Information lost through a helper | Does the signature communicate what the implementation establishes? | Add a useful annotation, `TypeGuard`, overload, or generic relationship |
| Unsupported or buggy inference | Does a small valid-Python reproducer fail with this exact checker/configuration? | A clear local guard or intermediate binding; otherwise a scoped workaround |
| Missing or inaccurate dependency types | What does the installed API actually accept and return? | Correct local stubs or a small adapter, based on evidence |
| Dynamic input that is genuinely unknown | Has the value been validated at all? | Parse serialized data with Pydantic; contain unknown SDK values inside an adapter |
| A checker-accepted runtime failure | Which assumption is not enforced by the type system? | Runtime validation or a behavioral test; do not manufacture a static guarantee |

First reproduce the CLI result in the project environment. Check the interpreter,
checker version, dependency/stub versions, and effective configuration. An editor
using a different environment is not evidence that the code needs a new abstraction.
Reduce the case before declaring either the program or the checker wrong.

## Example 1: a predicate's return annotation loses information

A function returning `bool` says only whether its condition holds. An ordinary
caller cannot assume that the checker will inspect its body and propagate a string
test performed inside it. When a reusable predicate really establishes a type,
`TypeGuard` makes that contract explicit. For a single use, an inline `isinstance`
check is often simpler than introducing a predicate at all.

The example narrows a known `str | int` union. Arbitrary external records belong
at a Pydantic boundary; the mapping-pattern defect below is a separate reproduction.

[Source](../examples/checker_limits.py)

```python
"""Express supported narrowing without casts or project-wide suppressions."""

from typing import TypeGuard


def is_nonempty_text(value: str | int) -> TypeGuard[str]:
    """Identify strings with visible content; promise only str to the checker."""
    return isinstance(value, str) and bool(value.strip())


def normalize_name(value: str | int) -> str:
    """Strip a validated name; raise ValueError for other values."""
    if is_nonempty_text(value):
        return value.strip()
    raise ValueError("name must be nonempty text")


name = normalize_name(" training ")
# rejected[bad-assignment]: count: int = name
```

With `TypeGuard[str]`, `normalize_name(" training ")` returns `"training"` and
passes checking. Replacing the predicate's return annotation with `bool` produces
`missing-attribute` at `value.strip()`: the caller still sees `str | int`, and
`int` has no `strip` method.

`TypeGuard` is a promise made by the predicate author. It does not cause the checker
to prove that a complicated validator is correct, and `TypeGuard[str]` does not
encode the additional nonempty-string property. Test the predicate's behavior;
do not use an always-true guard as a disguised cast.

## Example 2: valid Python rejected by the pinned checker

In Pyrefly **1.3.1**, matching a mapping against an `object` parameter produces
`not-callable`, referring to `__getitem__` and `Never`. The same Python code
executes successfully for a valid mapping: `case {"name": str(name)}` followed by
`return name.strip()` extracts `"training"` from `{"name": " training "}`.
The checker instead reports `not-callable` at that case. This deliberately unknown
parameter isolates a checker defect; it is not a recommended application API.

This is observed behavior of the pinned release, not a claim about every Pyrefly
version or a reported upstream issue number. Application examples use precise
unions or Pydantic parsing instead. The reproduction remains isolated so it does
not require weakening their types.

The reproduction test deliberately expects the known diagnostic. If an upgrade
fixes the checker, that test fails and prompts review: remove the limitation test
or update it to require acceptance. Do not restore a bug just to preserve the old
expectation.

## Example 3: the dependency stub is wrong

A dependency's `output_name()` returns `"embedding"`, but its stub declares
`def output_name() -> int: ...`. The caller writes `name: str = output_name()`.

| Stub return type | Checker result | Runtime result |
| --- | --- | --- |
| Incorrect `int` | `bad-assignment`: an `int` cannot be assigned to `str` | `"embedding"` |
| Corrected `str` | Accepted | `"embedding"` |

Changing the stub repairs the contract without changing the caller.

For a real dependency, first verify the installed version's behavior and documented
contract. Keep a narrow, version-compatible `.pyi` in a dedicated stub directory,
configure Pyrefly's `search-path` to find it, and test the interface it describes.
A stub can shadow a module's other type information, so preserve the API surface
your application uses rather than accidentally deleting it from the checker's view.

A local stub is appropriate for a known signature. If the SDK returns arbitrary
JSON text, parse it directly with Pydantic. For undocumented Python values, keep
the unknown result inside a small adapter and immediately validate it. Claiming
it returns a trusted domain record merely hides the uncertainty. Never edit
installed files inside `.venv` as the project's durable fix.

## Example 4: a narrow suppression is sometimes cleaner

For an unavoidable integration seam with a reproduced checker defect, a
documented line-level suppression can be preferable to a distorted API. This
patch illustrates the fallback on the isolated reproduction:

```diff
     match payload:
+        # Reproduced with Pyrefly 1.3.1; valid Python mapping pattern.
+        # Remove when the mapping-pattern regression accepts the unguarded source.
+        # pyrefly: ignore[not-callable]
         case {"name": str(name)}:
             return name.strip()
```

The suite applies this fallback only to a temporary copy of the reproduction. It
verifies that the specific diagnostic disappears, then adds an unrelated bad
assignment and verifies that it still fails. The application example needs
neither the unknown input nor a suppression.

Pyrefly supports code-specific suppressions, and the project enables `unused-ignore`
as an error so obsolete suppressions become visible. This is narrower than silencing
a file, excluding a package, or turning off an error category for the whole project.
[Pyrefly suppression documentation](https://pyrefly.org/en/docs/error-suppressions/).

Place the rationale beside the suppressed operation. Record the reproducer or real
upstream issue, affected versions, runtime evidence, and removal condition. Do not
invent an issue reference or describe an uninvestigated mismatch as a checker bug.

## A cast has a different job

`cast(T, value)` asks the checker to trust a type assertion. It does not validate,
convert, copy, or narrow the runtime object. It can be defensible when an invariant
has already been established but cannot be expressed to the checker, or inside a
small adapter for an accurately understood dynamic API.

Before adding one, state how the invariant is established. Keep the target type
precise, place the cast at the boundary that owns that evidence, and test the
observable contract. Do not distribute the same cast across every caller.
If the invariant is unknown, use validation instead. If only one erroneous
diagnostic is the issue, a specific suppression may express the workaround more
honestly than changing the inferred type.

There is no cast in this page's runnable example: its two cases have simpler fixes.
That does not make a cast categorically forbidden in a different, justified case.

## Keep the rest of the project clean

- Keep vendor-specific workarounds in adapters or local stubs, not in domain models
  or every call site. A small local typing limitation can stay beside its operation.
- Preserve the public behavior. Do not change errors, coercion, copying, or accepted
  inputs solely because a particular spelling checks more easily.
- Avoid new protocols, subclasses, wrappers, and duplicated algorithms whose only
  purpose is evading one diagnostic. Improve a signature when it conveys real information.
- Keep checks enabled for the surrounding code. Do not replace the dependency with
  `Any` or create a growing block of unrelated ignores.
- Test the boundary at runtime as well as statically. A correctly typed stub and
  a passing checker do not establish that the installed library honors the stub.
- Review the workaround on checker/dependency upgrades. Keep the reproduction
  small enough that removal is straightforward.

These decisions need not become a new framework. Often the right outcome is one
annotation, one guard, one adapter, or one justified comment.

## The opposite problem: wrong code can pass

A `float` annotation permits an integer, but the runtime pattern `float(score)`
does not match `0`. A handler needs both integer and float patterns. See
[the numeric edge case](practical-choices.md#match-every-runtime-representation-the-annotation-accepts).
