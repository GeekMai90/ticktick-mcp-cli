# Installation

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
