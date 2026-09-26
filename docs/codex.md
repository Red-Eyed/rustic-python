# Use the guide in Codex

[Project overview and reading path](../README.md)

The `rustic-python` skill helps Codex apply the guide to Python implementation
and review tasks. It loads relevant chapters on demand and includes the examples,
tests, and configuration templates locally. It does not replace your project's
instructions or automatically install tutorial dependencies into your application.

## Install from a checkout

With uv and Make available, run from this repository:

```sh
make install-skill
```

This builds the skill and links it into `~/.agents/skills/rustic-python`.
Keep this checkout: the link points to `build/skills/rustic-python` inside it.
Rerunning the command refreshes the bundled guide after you update the checkout.
An existing unrelated installation is never overwritten.

For a project-scoped installation, set the destination explicitly:

```sh
SKILLS_DIR=/path/to/your/project/.agents/skills make install-skill
```

Remove only the installed symlink to uninstall. Other skills and project settings
are unaffected. Codex normally detects new skills automatically; restart Codex
if it does not appear.

## Install a standalone snapshot

The published book includes a [downloadable skill bundle](https://red-eyed.github.io/rustic-python/downloads/rustic-python.zip).
Extract its `rustic-python` directory into `~/.agents/skills/` or your project's
`.agents/skills/`. This snapshot works without a checkout or network connection.
To update it, replace only that skill folder with a newer bundle after preserving
any edits you made. Do not place a snapshot over an existing symlink installation.

## Use it

In Codex CLI or the IDE extension, mention the skill:

```text
$rustic-python review this preprocessing pipeline for unsafe boundaries
$rustic-python design a small protocol for interchangeable feature extractors
$rustic-python improve these pytest fixtures without adding unnecessary layers
```

Codex can also select it when a request matches the skill description. The skill
routes to specific topics; installing it does not load the whole book into every
conversation. Its bundled tool settings are templates to adapt, not instructions
to overwrite your configuration.

See [official Codex skill documentation](https://learn.chatgpt.com/docs/build-skills)
for discovery, scope, and invocation. A plugin can distribute the same skill more
broadly later; this project currently provides a directly installable local skill.
