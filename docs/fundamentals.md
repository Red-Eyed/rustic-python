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
correct, or retry it, return a typed success-or-failure outcome. The checker can
then reject using the success value before handling the failure. Merely replacing
a late `KeyError` with a late `ValueError` does not meet this guide's goal.

Static checks do not establish that an algorithm is logically correct. They also
cannot prove numerical correctness, tensor shapes, or that Python will never
raise. Each lesson identifies the exact mistake made checkable and names the
runtime obligations that remain.
