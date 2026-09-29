# Catch mistakes before execution

[Project overview and reading path](../README.md)

A job has a name and a worker count. A caller reads `worker_count`, although the
field is named `workers`. If the record declares its fields, a type checker can
reject that typo before the job starts.

That is the purpose of this book: move mistakes from runtime discovery into
checked contracts. Each lesson models a situation, shows typical Python, then
shows an alternative and the exact misuse it rejects.

Not every property is static. A declared integer still needs runtime validation
if it must be positive. A correctly typed calculation can still be wrong. Each
lesson names the remaining obligation instead of promising exception freedom
or Rust's ownership guarantees.

Start with [validated records](data-modeling.md). Strengthen a type when it prevents
a concrete mistake; keep an ordinary function when it already expresses the contract.
