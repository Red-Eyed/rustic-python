# Move type-checkable mistakes into static checks

[Project overview and reading path](../README.md)

**The purpose of this guide is to make type-checkable mistakes fail static checks
instead of surfacing only when Python runs.** Every example is one view of that
goal: a misspelled field, an unhandled failure, an invalid state transition, or
an incompatible plugin.

For example, `metadata["worker_count"]` can raise `KeyError` after a job starts.
If the record declares a `workers` field, the checker rejects
`metadata.worker_count` before the job starts. The [record lesson](data-modeling.md)
shows both programs and the rejected operation.

External data can still be malformed at runtime; a checker cannot inspect JSON
that has not arrived yet. Validate it at the boundary. When the caller can reject,
correct, or retry it, return a typed success-or-failure outcome. The guide borrows
`Result<T, E>` from Rust's standard library: `Ok` carries a value and `Err`
carries an expected error.
Python has no built-in `Result`, but a small `Ok[T] | Err[E]` union makes the same
choice visible to the checker. A caller can use `match` to handle both cases;
`assert_never` checks that its branches cover the union. See the [Result and
match example](errors-and-absence.md) before the other data lessons.

That is why the guide is called *Rustic Python*: it borrows explicit outcomes,
closed variants, and state-dependent types where they make misuse checkable. It
does not promise Rust's ownership rules or exception-free execution. Merely
replacing a late `KeyError` with a late `ValueError` would miss the point.

Static checks do not establish that an algorithm is logically correct. They also
cannot prove numerical correctness, tensor shapes, or that Python will never
raise. Each lesson identifies the exact mistake made checkable and names the
runtime obligations that remain.
