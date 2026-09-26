# Use the guide in your coding agent

[Project overview and reading path](../README.md)

Give **Codex, Claude Code, or Cline** this message:

```text
Install the Rustic Python skill by reading and following:
https://raw.githubusercontent.com/Red-Eyed/rustic-python/main/INSTALL.md
```

The agent downloads the generated bundle, selects its own skill directory, and
verifies the installed references. You do not need to clone this repository,
install uv or just, or run setup commands. Add “for this project only” to the
message if you want a project-scoped installation. Ask the agent to “update”
instead of “install” when refreshing an existing copy.

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

## For contributors working from a checkout

The optional `just install-skill` recipe links a locally built bundle into
Codex's personal skill directory. To select a different host or project location,
set `SKILLS_DIR` to that host's skills directory. Keep the checkout while using
this linked installation; rebuilding refreshes its references. The downloadable
snapshot used by the agent installation flow does not depend on a checkout.
