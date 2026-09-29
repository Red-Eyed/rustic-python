# Instructions for coding agents

[Project overview and reading path](../README.md)

Use this page when applying the guide to another project. Read only the chapters
relevant to the task. The guide recommends an approach; the target project's
requirements, supported Python versions, and tools take precedence. Installing
the skill does not authorize replacing dependencies or refactoring unrelated code.

## Apply the guide

1. Name the concrete mistake to prevent and the caller's supported decisions.
   Choose the smallest representation that makes incorrect use a checker error.
   Add a wrapper or interface only when it prevents a specific checked mistake.
2. Preserve schemas and relationships in precise types. Validate unknown inputs
   at the boundary and contain library uncertainty there. Use the guide's Pydantic
   and pydantic-settings examples as the reference implementation, respecting the
   target stack. See [data modeling](data-modeling.md) and
   [settings](settings.md).
3. Declare recoverable failures as typed outcomes; let operations without a
   supported recovery path unwind. Use the small custom `Ok[T] | Err[E]` union
   when generic success/failure fits, with `match` and `assert_never`; no result
   base class, third-party result package, or unchecked unwrap is needed.
   A `Raises:` docstring is not a checked failure contract. See
   [Result and match](errors-and-absence.md) for recovery policy and the limits
   of this guarantee. Carry diagnostic details in typed error variants.
4. Keep reflection out of ordinary application logic. Use declared fields,
   explicit variants, and typed registries; contain necessary dynamic behavior
   in documented adapters or tests. See
   [dynamic access](dynamic-access.md).
5. Introduce protocols at real substitution points and separate types for useful
   lifecycle restrictions. Preserve behavioral contracts as well as signatures.
   See [composition](composition.md), [state](state-and-generics.md), and
   [generics](generics.md).
6. Verify the promised rejection with the project's checker and the runtime
   obligations with relevant tests. Investigate
   [checker limitations](checker-limitations.md) before adding suppressions.

## Report the result

Explain which mistake is now rejected, what is validated at runtime, and what
remains a convention or caller obligation. Static acceptance does not establish
exception freedom, ownership, or numerical correctness. Keep native tensors in
scientific code and test numerical behavior separately.

Use the [review checklist](checklist.md) for the final pass. Detailed chapter
contracts take precedence over an abbreviated summary; do not invent a new
framework or enforcement tool merely to apply this guide.
