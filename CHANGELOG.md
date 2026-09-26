# Changelog

## [Unreleased]

### Highlights

- Add a practical guide to Rust-inspired Python types and design, with ML and
  data science examples and explicit limits on what static checking guarantees.

### Documentation

- Organize the guide into topic pages covering records, sum types, errors,
  absence, state transitions, generics, immutability, protocols, and plugins.
- Demonstrate validation around untyped third-party code, including unknown
  payloads, exceptions, mutation, and inaccurate type stubs.
- Explain edge cases, acceptable simplifications, checker limitations, and the
  runtime checks still needed for numerical and tensor correctness.
- Add pytest lessons covering fixture dependency graphs, `conftest.py`,
  parametrization, resource cleanup, and testing anti-patterns.
- Explain where supplementary libraries such as Expression and more-itertools
  help, alongside their limitations.

### Developers

- Add runnable Python 3.11-compatible examples with deliberately invalid cases
  that tests verify against their expected Pyrefly diagnostics.
- Add strict Pyrefly and Ruff configurations with locked development and example
  dependencies managed by uv.
- Add behavioral tests and checks that documentation snippets match executable
  sources, including reproductions for checker and stub workarounds.
- Add repository-specific agent instructions and contribution guidance for
  extending the guide without weakening its contracts.
