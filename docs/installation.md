# Installation

For the shortest agent-oriented path, start with [Agent-First Quickstart](agent-quickstart.md).

## Installer script

For a one-command setup with the MCP server and keyring extras, run:

```bash
curl -fsSL https://raw.githubusercontent.com/GeekMai90/ticktick-mcp-cli/main/scripts/install.sh | sh
```

The script installs from this GitHub repository by default (`ticktick-mcp-cli[mcp,keyring] @ git+https://github.com/GeekMai90/ticktick-mcp-cli.git`) because the PyPI package name is not published yet. It prefers `uv tool install`, falls back to `pipx install`, and prints the verification commands below.

## GitHub npx wrapper for agents

Agent runtimes that already have Node.js can launch the wrapper directly from GitHub without a global npm registry package:

```bash
npx github:GeekMai90/ticktick-mcp-cli doctor --json
npx github:GeekMai90/ticktick-mcp-cli auth status --json
npx --package github:GeekMai90/ticktick-mcp-cli ticktick-mcp
```

The wrapper prefers `uvx --from 'ticktick-mcp-cli[mcp,keyring] @ git+https://github.com/GeekMai90/ticktick-mcp-cli.git' ...` and falls back to `python3 -m pipx run --spec 'ticktick-mcp-cli[mcp,keyring] @ git+https://github.com/GeekMai90/ticktick-mcp-cli.git' ...`. It does not store credentials; it only delegates to the Python CLI/MCP package.

## Install from GitHub source

Use the repository source until the `ticktick-mcp-cli` package is published on PyPI:

```bash
uv tool install 'ticktick-mcp-cli[mcp,keyring] @ git+https://github.com/GeekMai90/ticktick-mcp-cli.git'
# or
pipx install 'ticktick-mcp-cli[mcp,keyring] @ git+https://github.com/GeekMai90/ticktick-mcp-cli.git'
```

If you do not need keyring support, install only the MCP extra:

```bash
uv tool install 'ticktick-mcp-cli[mcp] @ git+https://github.com/GeekMai90/ticktick-mcp-cli.git'
# or
pipx install 'ticktick-mcp-cli[mcp] @ git+https://github.com/GeekMai90/ticktick-mcp-cli.git'
```

## Install from PyPI after publication

The repository has PyPI/TestPyPI release automation, but `ticktick-mcp-cli` is not installable from PyPI until a maintainer publishes a release. After publication, these commands should work:

```bash
uv tool install ticktick-mcp-cli
# or
pipx install ticktick-mcp-cli
```

Verify the installation:

```bash
ticktick-mcp-cli --version
ticktick-mcp-cli doctor --json
ticktick-mcp-cli auth status --json
```

## Development

```bash
uv sync --all-extras --dev
uv run pytest -q
uv run ticktick-mcp-cli --help
uv run tt --help
```

## Build from source

```bash
uv build
```

This creates a source distribution and wheel under `dist/`. Build artifacts are ignored by git.

## Optional MCP Support

The MCP server depends on the optional `mcp` package:

```bash
uv sync --extra mcp
uv run ticktick-mcp
```

Without the optional package, `ticktick-mcp` prints an installation hint instead of a Python stack trace.

## Local Config

Config is stored at:

```bash
uv run ticktick-mcp-cli config path
```

Set `TICKTASK_CONFIG_DIR` to override the config directory for tests or isolated runs.
