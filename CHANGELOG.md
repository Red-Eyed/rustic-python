# Changelog

## [Unreleased]

### Highlights

- Add an online book with chapter navigation and search, plus an offline Codex
  skill generated from the same maintained guide.
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

- Add agent-operated installation instructions for Codex, Claude Code, and Cline;
  readers give their agent a link instead of running setup commands.
- Replace Make targets with just recipes for checks, book builds, and skill
  installation; install just automatically in the GitHub Actions workflow.
- Add book and skill build targets, safe local skill installation, and GitHub
  Actions checks with GitHub Pages deployment for successful main builds.
- Use one project dependency list with minimum versions; keep exact resolutions
  in `uv.lock`.
- Keep pytest discovery and strictness settings in a standalone `pytest.ini`.
- Add runnable Python 3.11-compatible examples with deliberately invalid cases
  that tests verify against their expected Pyrefly diagnostics.
- Add strict Pyrefly and Ruff configurations with locked development and example
  dependencies managed by uv.
- Add behavioral tests and checks that documentation snippets match executable
  sources, including reproductions for checker and stub workarounds.
- Add repository-specific agent instructions and contribution guidance for
  extending the guide without weakening its contracts.
