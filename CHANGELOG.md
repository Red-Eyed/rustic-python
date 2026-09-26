# Changelog

Changes are grouped by commit, newest first. Dates come from Git history.

## [4a36831](https://github.com/Red-Eyed/rustic-python/commit/4a36831b801537d48e22115c04322b544dc5e0f0) — 2026-09-26

**Recoverability determines failure representation — 0.5.3**

- Use typed outcomes for supported recovery decisions, including retry, fallback,
  corrected input, and rejecting a record while processing continues.
- Reserve exceptions for operations with no meaningful recovery path that must
  unwind. Clarify that an outer boundary can still clean up, report, or isolate
  the failure; an exception does not require terminating the entire process.
- Replace the expected/unexpected-only rule throughout the guide and skill;
  synchronize the project and lockfile version at `0.5.3`.

## [12c0a73](https://github.com/Red-Eyed/rustic-python/commit/12c0a733fbe482ea6edea9ad61c98d9550d6c7cc) — 2026-09-26

**Expected failures as data — 0.5.2**

- Reserve application exceptions for unexpected failures and violated internal
  assumptions. Represent anticipated failures as typed outcomes even when the
  caller chooses to stop rather than recover.
- Explain translating anticipated library errors at application boundaries and
  distinguish invalid external input from broken internal preconditions.
- Align the errors lesson, decision guide, checklist, and agent/skill instructions;
  synchronize the project and lockfile version at `0.5.2`.

## [1f0a733](https://github.com/Red-Eyed/rustic-python/commit/1f0a7338cf7a4a7d54bdfffc7340f838d6d5177b) — 2026-09-26

**Statically checked failure contracts — 0.5.1**

- Center result guidance on rejecting misuse before execution: unchecked success
  access, confused payload types, and incomplete variant handling.
- Recommend typed outcomes for expected failures callers should handle, replacing
  the blanket preference for exception propagation. Keep unexpected exceptions
  visible and distinguish static contracts from runtime input validation.
- Update the guide and skill to require evidence of rejected misuse; synchronize
  the project and lockfile version at `0.5.1`.

## [f3d2b1b](https://github.com/Red-Eyed/rustic-python/commit/f3d2b1bb242402a7ecc53f9568010fd0b27dae26) — 2026-09-26

**Optional custom result unions — 0.5.0**

- Remove the returns and Expression dependencies and the Expression comparison.
  The result lesson now defines independent frozen `Ok[T]` and `Err[E]` records
  with `Result[T, E]` as a union alias, without a shared result base class.
- Replace `Success`/`Failure` and extraction methods with `Ok(value=...)` and
  `Err(error=...)` pattern matching. Readers adapting the old lesson should handle
  each variant explicitly; the custom records provide no map or unwrap methods.
- Verify generic payload contracts, rejection of unchecked field access, and
  exhaustive matching. Preserve exception tracebacks and notes in error payloads;
  callers explicitly raise from a stored exception when chaining is needed.
- Prefer exceptions for propagation and domain outcomes for failures callers
  inspect or collect. Present generic Result as an optional lesson rather than
  the default for every fallible function, including in agent and skill guidance.
- Synchronize the manifest and lockfile at `0.5.0`; verify 220 tests on Python 3.11.

## [0e98f80](https://github.com/Red-Eyed/rustic-python/commit/0e98f80af42bbb940aa0374c41242f64353fc1bc) — 2026-09-26

**Dynamic attribute access policy — 0.4.1**

- Restrict `getattr`, `setattr`, `hasattr`, `delattr`, and equivalent reflection
  in application logic; recommend declared fields, protocols, variants, and typed
  registries instead.
- Explain documented exceptions for unavoidable integration boundaries and tests
  that deliberately exercise dynamic behavior. Identify the restriction as design
  and review guidance rather than a static guarantee.
- Include the policy in the boundary chapter, checklist, agent guide, and portable
  skill; update the project and lockfile version to `0.4.1`.

## [5fed7b8](https://github.com/Red-Eyed/rustic-python/commit/5fed7b83804dfa1a8fdc998fab28568119f877a7) — 2026-09-26

**Precise application boundaries — 0.4.0**

- Change `parse_metadata`, `parse_task`, and `prepare_inference` to accept JSON
  text instead of arbitrary Python values. Callers copying these examples should
  pass the serialized input directly to Pydantic rather than decode it first.
- Replace `VendorCall` and `predict(request, vendor)` with a bound `Predictor`:
  use `vendor = bind_vendor(sdk_call)`, then `vendor(request)`. The callable returns
  validated outcomes; response parsing is private to the adapter.
- Keep unknown library values inside integration seams and narrow the settings
  validator's output to `int`. Move the mapping-pattern checker reproduction
  into the test harness and use a precise union in the runnable lesson.
- Load the installation destination through pydantic-settings while preserving
  the `SKILLS_DIR` override and default location.
- Update linked lessons, agent guidance, and static and runtime regression cases;
  verify 223 tests on Python 3.11 and synchronize the manifest and lockfile version.

## [8205663](https://github.com/Red-Eyed/rustic-python/commit/8205663ca6fea4307c856bb6c5a5482ae0670b97) — 2026-09-26

**Design and review checklist**

- Add paired Do / Avoid checks for data contracts, results and matching,
  boundary validation, component design, state, and testing.
- Link each topic to its detailed lesson and make the checklist accessible from
  the README, book navigation, and coding-agent instructions.
- Preserve guidance on acceptable simplifications and the limits of static
  guarantees; update the project version to `0.3.3`.

## [f8bae47](https://github.com/Red-Eyed/rustic-python/commit/f8bae474511fef32da6c3601e9a253a14348707e) — 2026-09-26

**Library result types and preserved failure diagnostics**

- Replace custom generic Ok/Err/Result definitions with returns' `Result`,
  `Success`, and `Failure`; update the guide and agent recommendations.
- Explain that unchecked unwrapping can raise and that returns does not provide
  the exhaustive-matching guarantee of a closed Python union.
- Demonstrate typed mapping and explicit handling of both outcomes, with tests
  for invalid labels and unchecked extraction.
- Explain preserving caught exceptions, tracebacks, Python 3.11 notes, and data
  provenance; cover logging and the memory cost of retaining tracebacks.
- Add returns to the dependencies and update the project version to `0.3.2`.

## [b9108ac](https://github.com/Red-Eyed/rustic-python/commit/b9108aca14920494b8273c03338f9898f436995a) — 2026-09-26

**Automatic skill freshness checks**

- Instruct installed skills to check GitHub before each task and refresh
  unchanged managed copies, then reread the updated guide.
- Include the source commit, dirty-build flag, and file hashes in skill bundles.
- Use a commit-pinned repository snapshot when the published ZIP lags behind;
  preserve local edits and report when offline freshness cannot be verified.
- Document backups, explicit pins, and the one-time update needed by older
  installations that lack refresh instructions.
- Verify bundle provenance and edit detection; update the version to `0.3.1`.

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
