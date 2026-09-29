# How to read the examples

[Project overview and reading path](../README.md)

Each recommendation follows one situation: typical Python, a better alternative,
and what changes for the caller. Short sketches omit imports and unrelated
setup. Each Source link opens the complete checked example within the book;
you do not need Python, a terminal, or a repository clone.

A line such as `# rejected[missing-attribute]: workers = outcome.workers`
means the checker rejects the statement after the colon. Here the model declares
`workers`, but the outcome might be `InvalidMetadata`. The diagnostic category is
shown so the result is visible without running anything. These comments are not
suppressions.

The examples use Python 3.11+, Pyrefly 1.3.1, and Ruff 0.16.9. Pydantic validates
external inputs; pytest checks behavior. These are the book's reference tools,
not reader prerequisites. [Contributor checks](contributing.md) verify source
links, runtime behavior, and the intended diagnostic for each rejected statement.
