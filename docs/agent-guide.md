# Instructions for coding agents

[Project overview and reading path](../README.md)

Use this section as a project prompt or reference it from the project's agent
instructions. Repository-specific requirements take precedence over this guide.

Use the [design and review checklist](checklist.md) to check positive practices
and what to avoid before handing off a change. Apply only the relevant items.

1. Identify the domain invariant before choosing the type. Explain a concrete mistake
   the representation should prevent.
2. Keep required identity and schema fields required. Use typed variants for real
   alternatives and reason-carrying absence for domain values.
   Expected failures are data; reserve exceptions for unexpected failures and
   violated internal assumptions. Declare anticipated failures as typed outcomes,
   even when the caller will stop rather than recover. Catch specific
   expected exceptions at boundaries; do not disguise programming defects as
   routine errors or claim that Result prevents all exceptions. Use the custom
   `Result` union when generic success/failure fits the contract. Its `Ok[T]` and
   `Err[E]` variants are frozen dataclasses. Use structural pattern matching
   and `assert_never`; avoid a shared result base class, third-party result
   packages, and unchecked unwrap methods.
3. Annotate function boundaries and structured records. Preserve generic
   relationships. Keep `Any` and `object` out of application APIs. Parse serialized inputs directly
   with Pydantic; contain unavoidable unknown library values inside a small adapter
   that immediately returns precise types. Do not introduce casts or ignores to silence
   unexplained diagnostics. For a verified limitation, use the smallest justified
   workaround described in [checker limitations](checker-limitations.md).
4. Validate external schemas with Pydantic at the boundary and load environment
   configuration with pydantic-settings. Build CLIs with its `CliApp`, typed
   arguments, flags, and subcommands instead of hand-written argparse.
   Use discriminated unions for tagged
   payload alternatives. Select coercion and extra-field policies explicitly.
   Keep validation outside numerical and compiled inference code; pass native
   tensors and plain `NamedTuple`/`TypedDict` records there. Keep pure transformations
   separate from filesystem, network, logging, and training orchestration concerns.
5. Use `match` for variant dispatch and `assert_never` for exhaustive closed unions.
   Do not add a catch-all value that silently accepts future variants.
6. Prefer frozen records and immutable members when mutation is unnecessary.
   Explain aliasing and mutation explicitly when arrays or tensors are involved.
7. Introduce small protocols only where callers need substitution. Signature
   compatibility does not replace behavioral contracts or tests.
8. Run Pyrefly, Ruff, and relevant behavioral tests. A static guarantee needs an
   intentionally broken example rejected for the intended reason, as well as a
   passing example. A missing import is not evidence of the desired rejection.
9. Report guarantees accurately: **statically checked**, **runtime validated**, or
   **convention only**. Never describe the implementation as borrow-checked or
   scientifically correct merely because tooling passes.
10. Keep changes focused. Do not build an imitation Rust standard library when a
    local dataclass, union, or ordinary function expresses the contract clearly.
    Keep native tensors and arrays in numerical code; do not create semantic
    wrappers for every intermediate. A nominal type needs a concrete boundary
    benefit that outweighs its propagation and maintenance costs.
11. Prefer protocols and composition at extension points. Choose a closed sum type
    when every alternative must be known; choose an open protocol for independent
    implementations. Use established supplementary libraries when their verified
    contracts fit, rather than rebuilding a collection of utilities.
12. Test runtime contracts with pytest. Compose fixtures by requesting fixtures,
    keep shared setup in the nearest `conftest.py`, and parametrize repeated cases.
    Assert observable behavior; do not call fixtures manually or hide the operation
    under test inside a result fixture.
13. State relevant edge cases and acceptable simplifications. Prefer plain values
    and functions where they express the contract. Reserve exceptions for unexpected
    failures and broken assumptions; keep expected failures in typed outcomes. Escalate to
    wrappers, variants, or protocols for a demonstrated need, not resemblance to
    Rust. Use the [decision guide](practical-choices.md), and never simplify away a
    failure, absence reason, or data-handling policy that callers need.
14. Treat checker output as evidence to investigate. Reproduce suspected tool/stub
    defects, preserve the application's contract, and localize workarounds with
    tests and a removal condition. Do not redesign a clean API around one checker bug.
15. Restrict dynamic attribute access: do not use `getattr`, `setattr`, `hasattr`,
    or `delattr` in application logic, or bypass declared contracts through `vars`,
    `__dict__`, or dynamic attribute hooks. Prefer direct access, small protocols,
    explicit variants, and typed registries. Allow only localized, documented
    integration seams or tests that need reflection; validate external values and
    return precise types. See [the boundary policy](third-party-boundaries.md#restrict-dynamic-attribute-access).
