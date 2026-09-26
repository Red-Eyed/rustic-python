# Use the guide in your coding agent

[Project overview and reading path](../README.md)

Give **Codex, Claude Code, or Cline** this message:

```text
Install the Rustic Python skill by reading and following:
https://raw.githubusercontent.com/Red-Eyed/rustic-python/main/INSTALL.md
```

The agent checks the repository revision, downloads the matching references,
selects its own skill directory, and verifies the installed files. You do not need to clone this repository,
install uv or just, or run setup commands. Add “for this project only” to the
message if you want a project-scoped installation. Installing opts into automatic
reference updates before use. For older installed copies that lack this behavior,
ask the agent to “update” once using the same link.

[Read the installation instructions](../INSTALL.md) to see exactly what the
agent will do. The same portable `SKILL.md`, chapters, examples, and templates
work across all three hosts. This requires an agent with file and network tools;
the host may ask for its normal permissions.

## Use it

| Host | Example |
| --- | --- |
| Codex | `$rustic-python review this preprocessing pipeline` |
| Claude Code | `/rustic-python review this preprocessing pipeline` |
| Cline | Select `/rustic-python` in chat and request the review |

The skill loads relevant chapters on demand. Installing it does not load the
whole book into every conversation or replace your project's instructions.
Its tool settings are templates to adapt, not instructions to overwrite your
configuration. Installed references remain available offline.

Host documentation: [Codex](https://learn.chatgpt.com/docs/build-skills),
[Claude Code](https://code.claude.com/docs/en/skills), and
[Cline](https://docs.cline.bot/customization/skills).

## Automatic updates

At the start of each task using the skill, the agent compares the installed Git
revision with GitHub `main`. It refreshes an unchanged managed installation before
reading chapters and rereads the new skill instructions. This is an agent workflow,
not a background service or a timer. It needs the host's file and network tools.

Bundles contain `rustic-python-source.json` with the source commit, a dirty-build
flag, and file hashes. The agent uses a commit-pinned repository archive when the
Pages ZIP has not caught up. That fallback reflects `main` without claiming its
CI build has completed. Package versions alone are not a freshness check.

An update preserves the previous installation in a backup outside skill discovery.
If files were edited, provenance is unknown, or the installation is a symlink,
the agent preserves it and uses a freshly staged snapshot for the task instead.
Explicitly requested replacement of an edited directory still requires a backup.
An explicit pin overrides automatic updates. Offline or blocked checks keep the
cached copy and disclose that freshness was not verified; they never silently
label it current.

## For contributors working from a checkout

The optional `just install-skill` recipe links a locally built bundle into
Codex's personal skill directory. To select a different host or project location,
set `SKILLS_DIR` to that host's skills directory. Keep the checkout while using
this linked installation; rebuilding refreshes its references. Automatic refresh
will not write through that link or update your checkout. The downloadable
snapshot used by the agent installation flow does not depend on a checkout.
