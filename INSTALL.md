# Install Rustic Python — instructions for coding agents

When the user asks you to install Rustic Python, perform the installation below
with your own file and terminal tools. Do not hand the user a list of shell
commands. This installs reference material, not Python dependencies.

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

## Download and install

1. Fetch the ready-made bundle:
   <https://red-eyed.github.io/rustic-python/downloads/rustic-python.zip>.
   Use a temporary directory and fail on unsuccessful HTTP responses. No clone,
   uv, just, Python environment, or execution of bundled code is required.
2. Inspect the archive before extracting. Entries must stay inside its single
   `rustic-python/` directory; reject absolute paths, parent traversal, and
   symlinks. Extract into the temporary directory, not directly over an existing
   installation.
3. Check that the extracted folder contains `SKILL.md` with
   `name: rustic-python`, `docs/`, `examples/`, `tests/`, and the three templates
   `pyrefly.toml`, `ruff.toml`, and `pytest.ini`. Read `SKILL.md` and verify its
   relative reference links resolve inside the extracted folder. Do not install
   only `SKILL.md`: it needs the bundled chapters and examples.
4. If the destination is absent, create its parent and move the complete skill
   folder there. If it already contains identical files, report it as current.
   If it differs, preserve it and report the conflict unless the user requested
   an update. For a requested update, preserve the old folder as a sibling backup
   before replacing it; report the backup path. Do not follow an existing symlink
   and overwrite its target.
5. Verify the installed `SKILL.md` and linked references are readable at the
   final path. Leave project settings, `AGENTS.md`, `CLAUDE.md`, `.clinerules`,
   other skills, and dependency environments untouched. Respect the host's normal
   file and network permissions.

## Report the result

Give the installed path, the bundle version from its `pyproject.toml`, and one
invocation example:

- Codex: `$rustic-python review this preprocessing pipeline`.
- Claude Code: `/rustic-python review this preprocessing pipeline`.
- Cline: select `/rustic-python` in chat, then request the review.

If the host exposes skill discovery, check that it lists `rustic-python`.
Otherwise report that the files are installed and ask the user to refresh the
skill list or restart the session only if it does not appear. Do not claim a
runtime activation test you did not perform.

For updates, the user can give you this same link and ask to update Rustic Python.
For removal, delete only the installed skill folder or symlink when requested.

Host references: [Codex](https://learn.chatgpt.com/docs/build-skills),
[Claude Code](https://code.claude.com/docs/en/skills), and
[Cline](https://docs.cline.bot/customization/skills).
