# Changelog

Changes are grouped by commit, newest first. Dates come from Git history.

## [06e8ad3](https://github.com/Red-Eyed/rustic-python/commit/06e8ad32d14e11a6bfec2c38907e1c66bbbd0317) — 2026-09-26

**Pydantic boundaries, settings, and inference contracts**

- Use Pydantic for external schemas and demonstrate classification/regression
  discriminated unions with exhaustive downstream handling.
- Add pydantic-settings configuration, source-precedence tests, and guidance to
  build CLIs with typed argument models instead of hand-written argparse.
- Demonstrate validation before a plain NamedTuple/TypedDict inference handoff;
  keep Pydantic outside compiled execution. The scalar example does not claim
  verified PyTorch compilation support.
- Change SDK response validation to reject extra fields and accept integer
  confidence endpoints as floats. Callers copying the example should remove
  unexpected response keys. Label parsing now accepts integer-valued decimal
  text such as `"7.0"`; fractional labels remain invalid.
- Document coercion, unchecked model construction, frozen-model limitations,
  and invalid settings and payload behavior, with 180 passing tests on Python 3.11.
- Replace Unreleased notes with commit-based history and update the project
  version to `0.3.0`.

## [bd956dc](https://github.com/Red-Eyed/rustic-python/commit/bd956dc) — 2026-09-26

**Agent-operated installation and just recipes**

- Add a single installation-instructions link for Codex, Claude Code, and Cline.
  The agent installs the ready-made bundle and verifies its references.
- Make agent-operated installation the primary README and book workflow.
- Replace Make with just for checks, book builds, and local skill installation;
  install just in GitHub Actions.
- Update the project version to `0.2.1`.

## [20f1f38](https://github.com/Red-Eyed/rustic-python/commit/20f1f38) — 2026-09-26

**Online book and portable Codex skill**

- Add an mdBook site with chapter navigation and search, built from the existing
  guide, plus GitHub Pages deployment after successful checks.
- Generate an offline skill bundle from the same chapters, examples, tests, and
  configuration templates; provide a downloadable ZIP and local installation.
- Check rendered links, chapter coverage, bundled references, and installation
  conflicts.
- Update the project version to `0.2.0`.

## [1d92499](https://github.com/Red-Eyed/rustic-python/commit/1d92499) — 2026-09-26

**Simpler tutorial configuration**

- Consolidate dependencies into one list with `>=` constraints; retain exact
  resolved versions in `uv.lock`.
- Allow newer Ruff and Pyrefly versions in their standalone configurations.
- Move pytest settings into `pytest.ini` and keep VS Code settings local.
- Update the project version to `0.1.2`.

## [abced5c](https://github.com/Red-Eyed/rustic-python/commit/abced5c) — 2026-09-26

**Initial practical typing guide**

- Add a general-purpose Rust-inspired Python guide with an ML and data science
  bias, organized into topic pages with a README entry point.
- Cover records, sum types, errors, absence, state, generics, immutability,
  protocols, composition, and plugins using runnable Python 3.11 examples.
- Demonstrate untyped third-party boundaries, checker limitations, numerical
  correctness constraints, edge cases, and acceptable simplifications.
- Add pytest lessons for fixture dependency graphs, parametrization, cleanup,
  and anti-patterns, alongside guidance on supplementary libraries.
- Add strict Ruff and Pyrefly configurations, uv tooling, and tests for runtime
  behavior, expected type errors, and documentation synchronization.
- Add agent instructions and contribution guidance; introduce version `0.1.1`.

## [9823996](https://github.com/Red-Eyed/rustic-python/commit/9823996) — 2026-09-26

- Initialize the repository with the MIT license.
