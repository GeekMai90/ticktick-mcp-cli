# Installation

## Development

```bash
uv sync --all-extras --dev
uv run pytest -q
uv run ticktask --help
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
uv run ticktask-mcp
```

Without the optional package, `ticktask-mcp` prints an installation hint instead of a Python stack trace.

## Local Config

Config is stored at:

```bash
uv run ticktask config path
```

Set `TICKTASK_CONFIG_DIR` to override the config directory for tests or isolated runs.
