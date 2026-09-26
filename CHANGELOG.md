# Changelog

Changes are grouped by commit, newest first. Dates come from Git history.

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
