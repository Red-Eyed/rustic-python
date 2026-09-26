# Install Rustic Python — instructions for coding agents

When the user asks you to install Rustic Python, perform the installation below
with your own file and terminal tools. Do not hand the user a list of shell
commands. This installs reference material, not Python dependencies. Installing
the skill opts into checking for and applying reference updates when it is used.
An explicit user request to pin a revision or disable updates takes precedence.

## Choose the destination

Use the host you are currently running in, not the model name or which programs
happen to be installed. Install for that host only, unless the user explicitly
asks for multiple hosts. Default to personal scope; honor a requested project
scope or explicit destination. Ask only if the host or requested location cannot
be determined from the conversation and environment.

| Host | Personal destination | Project destination |
| --- | --- | --- |
| Codex | `~/.agents/skills/rustic-python/` | `<project>/.agents/skills/rustic-python/` |
| Claude Code | `~/.claude/skills/rustic-python/` | `<project>/.claude/skills/rustic-python/` |
| Cline | `~/.cline/skills/rustic-python/` | `<project>/.cline/skills/rustic-python/` |

Expand `~` using the user's home directory, including on Windows. If the host has
an explicitly configured skills directory, use it. These instructions target
coding agents with local file access; a browser-only chat cannot install local
files and should say so rather than claim success.

## Check for updates before use

Check once at the beginning of each task using the skill, including when a new
task starts in an existing conversation. Use the folder from which this skill
was loaded; do not install a second copy into a different scope.

1. Fetch `https://api.github.com/repos/Red-Eyed/rustic-python/commits/main`
   with an HTTP client that checks status codes, a bounded timeout, and cache
   revalidation (`Cache-Control: no-cache`). Read the full 40-character hexadecimal
   `sha`. This is the target revision for this task. Use commit identity, not
   package versions or dates: documentation can change between version bumps.
   Before staging an update, read `INSTALL.md` from
   `https://raw.githubusercontent.com/Red-Eyed/rustic-python/<full SHA>/INSTALL.md`
   and use that revision's layout and update instructions. Keep the already
   resolved target SHA; do not restart the check recursively.
2. Read local `rustic-python-source.json`. Its format is `schema_version: 1`,
   `repository: "https://github.com/Red-Eyed/rustic-python"`,
   `source: {"commit": "<full SHA>", "dirty": false}`, and `files`, a mapping
   of relative POSIX file paths to SHA-256 hex digests. Verify file hashes before
   treating the installation as unchanged. Ignore only `__pycache__`,
   `.pytest_cache`, `.ruff_cache`, and `.pyc` files. Added, changed, missing, or
   symlinked reference files count as local modifications. The metadata file
   itself is excluded from its hash map. Digests detect edits, not authenticity.
3. If the repository matches, `source.dirty` is false, the commit matches the
   target, and the files are unchanged, continue using this copy. Otherwise stage
   the target using the next section. Missing or invalid metadata means unknown
   provenance, not a current installation.
4. Automatically refresh an unchanged managed installation, then reread the new
   `SKILL.md` and needed chapters. Keep this task's check result so rereading does
   not trigger an update loop. Report an update with its old/new revisions.

For a user-pinned copy, honor the pin and identify it as pinned. For local edits,
dirty builds, unknown provenance, or symlink installations, preserve the installed
copy and use the freshly staged reference folder for this task instead; report
its path and why the installed copy was not replaced. An explicitly requested
update may replace a legacy or edited directory after backing it up. Never write
through a symlink or change the user's checkout automatically.

If GitHub is unavailable, rate-limited, permissions are denied, or no valid staged
copy can be obtained, keep the existing copy and disclose its revision (if known)
and that freshness could not be verified. Do not claim an offline copy is current.
Do not loop on failures; retry on the next task. A first installation without a
valid source fails clearly instead of reporting success. Check again when the
user explicitly requests an update; otherwise do not poll throughout a task.

## Stage the target revision

Perform downloads and file operations yourself. No clone, project dependencies,
or execution of downloaded code is required.

1. Fetch the ready-made bundle into a temporary directory:
   <https://red-eyed.github.io/rustic-python/downloads/rustic-python.zip>.
   Require a successful HTTP response. Inspect the archive before extracting:
   reject absolute paths, parent traversal, symlinks, and duplicate destinations;
   every entry must stay within its single `rustic-python/` root.
2. Extract into staging. Accept this ZIP only when its metadata names the expected
   repository, records the target commit with `dirty: false`, and its complete
   file inventory and hashes match. Reject malformed metadata or escaping paths.
3. If Pages is unavailable or its ZIP does not match, fetch the repository archive
   for the **exact target SHA**, never a moving `main` archive:
   `https://api.github.com/repos/Red-Eyed/rustic-python/zipball/<full SHA>`.
   Follow GitHub's archive redirect and enforce the same extraction rules, allowing
   its single generated repository root name. This fallback avoids waiting for
   Pages deployment; it is repository content, not a claim that CI has passed.
4. Assemble a fresh `rustic-python/` folder from that archive: copy `README.md`,
   `CHANGELOG.md`, `LICENSE`, `INSTALL.md`, `pyproject.toml`, `uv.lock`,
   `pyrefly.toml`, `ruff.toml`, `pytest.ini`, and the `docs/`, `examples/`, `tests/`
   directories. Omit caches, `.pyc` files, and `tests/test_distribution.py`.
   Copy `skills/rustic-python/SKILL.md` to the folder's root as `SKILL.md`.
   Remove the README line beginning `- [AGENTS.md]`; do not copy repository
   maintenance instructions, `.git`, `tools/`, or host configuration.
5. For an archive-assembled copy, write the metadata format described above using
   the target SHA, `dirty: false`, and SHA-256 digests of all assembled files.
   Never relabel a stale Pages ZIP as the target revision.
6. Verify `SKILL.md` has `name: rustic-python`, required directories and templates
   exist, and its relative references resolve inside staging. Do not install just
   `SKILL.md`. A malformed published bundle may fall back to the repository archive;
   a malformed fallback must stop the update and preserve the existing copy.

The target is the revision observed at the start of the check. If `main` advances
while downloading, finish this consistent snapshot and check again next task.
Do not combine chapters from different revisions.

## Install or replace

For a new installation, choose the destination above. For an update, retain the
existing destination. Finish staging and validation before touching it.

Create its parent if needed. For replacement, recheck the installed file hashes
to catch edits made during downloading. If unchanged, move the old folder to a
unique backup outside the host's skill discovery directories, then move the
complete staged folder into place. If replacement or final verification fails,
restore the backup. Never merge files over the old directory: deleted chapters
must disappear too. Serialize updates to the same destination; if another agent
is updating it, use the staged snapshot for this task rather than racing it.

Verify the installed metadata, `SKILL.md`, and linked references at the final
path, then report the revision and backup path. Leave project settings,
`AGENTS.md`, `CLAUDE.md`, `.clinerules`, other skills, and dependency environments
untouched. Respect normal host file and network permissions; automatic refresh
does not bypass those permissions.

## Report the result

Give the installed path, the source commit, the version from `pyproject.toml`, and one
invocation example:

- Codex: `$rustic-python review this preprocessing pipeline`.
- Claude Code: `/rustic-python review this preprocessing pipeline`.
- Cline: select `/rustic-python` in chat, then request the review.

If the host exposes skill discovery, check that it lists `rustic-python`.
Otherwise report that the files are installed and ask the user to refresh the
skill list or restart the session only if it does not appear. Do not claim a
runtime activation test you did not perform.

Updates happen before skill use. Older copies without the refresh instructions
need a one-time update using this link. The user may also request an immediate
update or explicitly pin a revision.
For removal, delete only the installed skill folder or symlink when requested.

Host references: [Codex](https://learn.chatgpt.com/docs/build-skills),
[Claude Code](https://code.claude.com/docs/en/skills), and
[Cline](https://docs.cline.bot/customization/skills).

GitHub references: [commit lookup](https://docs.github.com/en/rest/commits/commits#get-a-commit)
and [commit-pinned archives](https://docs.github.com/en/rest/repos/contents#download-a-repository-archive-zip).
