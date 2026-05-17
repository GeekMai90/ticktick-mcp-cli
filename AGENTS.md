# AGENTS.md

## Project: TickTick MCP CLI

Build an open-source, agent-friendly CLI and MCP server for TickTick international and Dida365 domestic APIs.

## Required workflow

- Follow `docs/plans/2026-05-17-ticktask-cli-mcp-plan.md`.
- Use TDD for core behavior and CLI behavior.
- Keep CLI and MCP thin; put shared logic in `src/ticktask/core/`.
- Never commit real credentials, access tokens, refresh tokens, or user-local config.
- Support both service profiles:
  - `ticktick`: `https://api.ticktick.com`
  - `dida365`: `https://api.dida365.com`
- Machine-facing commands must support stable JSON output.
- Dangerous operations must avoid ambiguity and require explicit confirmation for non-interactive use.

## Verification before completion

Run:

```bash
uv run pytest -q
uv run ticktick-mcp-cli --help
uv run ticktick-mcp-cli doctor --json
uv run ticktick-mcp-cli auth status --json
```

If something cannot be implemented, document the reason in the final summary and leave tests for implemented behavior passing.
