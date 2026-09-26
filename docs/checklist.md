# Design and review checklist

[Project overview and reading path](../README.md)

Use this checklist when designing an API or reviewing a change. Check an item
when its positive practice is satisfied and its avoid case is absent. Skip items
that do not apply; do not add machinery just to satisfy the list. Each topic links
to the lesson explaining its tradeoffs and verified examples.

## Choose the contract

- [ ] **Do:** name the concrete mistake the representation should prevent and
  choose the simplest design that prevents it. **Avoid:** imitating Rust with a
  wrapper, protocol, or result container around every value and function.
  [Practical choices](practical-choices.md)
- [ ] **Do:** use precise records for shared schemas and keep required identity
  fields required. **Avoid:** passing loose dictionaries between helpers or making
  every field optional to accommodate malformed input.
  [Data modeling](data-modeling.md)
- [ ] **Do:** use precise domain types, including `date` and `datetime` for dates
  and timestamps, and enums or variants for meaningful alternatives. **Avoid:**
  string conventions that every consumer must remember and parse again.
  [Data modeling](data-modeling.md)
- [ ] **Do:** annotate function boundaries and preserve relationships between
  generic inputs and outputs. **Avoid:** erasing those relationships with `Any`
  or accepting combinations the operation cannot support.
  [State and generics](state-and-generics.md)

## Handle outcomes and alternatives

- [ ] **Do:** declare expected failures callers should handle as typed outcomes;
  use the small `Ok[T] | Err[E]` union when generic success/failure fits.
  **Avoid:** hiding expected alternatives in an exception-only API, converting
  programming defects into routine errors, or claiming Result prevents every
  possible exception. Keep the representation small.
  [Errors and absence](errors-and-absence.md)
- [ ] **Do:** extract payloads through structural pattern matching on the variant.
  **Avoid:** unchecked unwrap helpers, discarded outcomes, or claiming that a
  result return type proves the function cannot raise.
  [Result handling](errors-and-absence.md#make-expected-failures-explicit)
- [ ] **Do:** dispatch with `match` and use `assert_never` for statically closed
  unions, including `Result`. **Avoid:** catch-all branches that silently accept
  new alternatives or replacing a closed union with an open class hierarchy.
  [Data modeling](data-modeling.md), [Result handling](errors-and-absence.md)
- [ ] **Do:** preserve a meaningful absence reason and distinguish missing data
  from valid zero or empty values. **Avoid:** truthiness checks for presence,
  unexplained domain `None`, or zero as a substitute for an undefined metric.
  A standard API's local `None` can be handled immediately without a new domain type.
  [Reasoned absence](errors-and-absence.md#preserve-the-reason-a-value-is-absent)
- [ ] **Do:** retain error details and source coordinates callers need; preserve
  exceptions when their tracebacks are useful. **Avoid:** swallowing programming
  bugs, flattening every error into a string, or accumulating millions of tracebacks
  that retain large objects.
  [Failure provenance](errors-and-absence.md#know-where-a-failure-happened)

## Validate at boundaries

- [ ] **Do:** use declared fields, small protocols, explicit variants, or typed
  registries. **Avoid:** `getattr`, `setattr`, `hasattr`, `delattr`, or equivalent
  reflection in application logic. Permit only documented, localized framework
  adapters and tests that need dynamic behavior; expose precise types afterward.
  [Dynamic attribute access](third-party-boundaries.md#restrict-dynamic-attribute-access)
- [ ] **Do:** parse the concrete wire representation directly with Pydantic and
  expose precise types to application code. **Avoid:** `Any` or `object` in domain
  APIs; keep unavoidable library uncertainty inside a small integration adapter.
  [Data modeling](data-modeling.md)
- [ ] **Do:** validate external schemas with Pydantic and choose coercion,
  unknown-field, and missing-field policies explicitly. **Avoid:** treating an
  annotation or cast as runtime validation, or passing vendor payloads through the
  application as trusted records.
  [Third-party boundaries](third-party-boundaries.md)
- [ ] **Do:** use pydantic-settings for environment configuration and typed CLIs.
  **Avoid:** scattered environment parsing or a separate hand-written argparse
  schema that can drift from the application's model.
  [Settings and CLIs](state-and-generics.md)
- [ ] **Do:** keep filesystem, network, logging, and CLI output at the edges;
  inject dependencies where substitution is needed. **Avoid:** mixing pure
  transformations with backend calls or presentation policy.
  [Third-party boundaries](third-party-boundaries.md)
- [ ] **Do:** define behavior for relevant malformed, empty, nonfinite, and partial
  inputs. **Avoid:** silently dropping samples, coercing values, or retrying side
  effects without an explicit policy.
  [Edge cases](practical-choices.md#edge-cases-that-types-alone-do-not-settle)

## Keep components and state understandable

- [ ] **Do:** use small protocols at real substitution points and composition for
  added behavior; use closed unions when all alternatives must be known.
  **Avoid:** broad interfaces, unnecessary inheritance, or a protocol for every
  ordinary function.
  [Protocols and composition](oop-and-plugins.md)
- [ ] **Do:** require interchangeable implementations to preserve error behavior,
  mutation policy, and other observable contracts. **Avoid:** treating matching
  method signatures as sufficient evidence of substitutability.
  [Protocols and composition](oop-and-plugins.md)
- [ ] **Do:** encode lifecycle restrictions in distinct states when callers would
  otherwise repeat guards. **Avoid:** interacting flags and optional fields that
  admit invalid states; keep a local guard when it fully contains the restriction.
  [State transitions](state-and-generics.md), [Simplifications](practical-choices.md)
- [ ] **Do:** prefer immutable records where suitable and make aliasing or copying
  policy explicit. **Avoid:** assuming a frozen dataclass freezes its contained
  lists, arrays, or tensors, or that validation survives later mutation.
  [Immutability limits](state-and-generics.md)
- [ ] **Do:** keep native tensors in numerical code and validation outside compiled
  inference; use plain `NamedTuple` or `TypedDict` records there when needed.
  **Avoid:** Pydantic construction in the compiled core or nominal wrappers for
  every intermediate without a demonstrated boundary benefit.
  [Scientific correctness](ml-correctness.md)

## Verify the promises

- [ ] **Do:** run the project's checker, linter, and relevant behavioral tests;
  verify promised static rejections fail for the intended reason. **Avoid:** treating
  a missing import or unrelated diagnostic as proof of a static guarantee.
  [Tooling](tooling.md), [Contributing examples](contributing.md)
- [ ] **Do:** reproduce suspected checker defects and keep workarounds narrow,
  tested, and tied to a removal condition. **Avoid:** unexplained casts, blanket
  ignores, relaxed strictness, or redesigning a clean API around a tool bug.
  [Checker limitations](checker-limitations.md)
- [ ] **Do:** test observable behavior, invalid inputs, and relevant numeric edge
  cases; parametrize repeated cases. **Avoid:** tests that merely mirror the
  implementation or check only the happy path.
  [Testing](testing.md), [Numeric edge cases](practical-choices.md)
- [ ] **Do:** compose fixtures through fixture arguments, keep shared setup in the
  nearest `conftest.py`, and ensure resource cleanup covers partial setup failures.
  **Avoid:** calling fixtures manually or hiding the action under test in a result
  fixture.
  [Pytest practices](testing.md)
- [ ] **Do:** label guarantees as statically checked, runtime validated, or
  convention only, and verify numerical behavior separately. **Avoid:** claiming
  passing types prove ownership, tensor shapes, finiteness, exception freedom,
  or correct training signals.
  [Scientific correctness](ml-correctness.md)
