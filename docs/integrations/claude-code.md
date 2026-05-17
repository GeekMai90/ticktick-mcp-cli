# Claude Code MCP Config

Claude Code can use TickTick MCP CLI as a local stdio MCP server when MCP servers are configured for the workspace or user environment.

## Prerequisites

```bash
uv tool install 'ticktick-mcp-cli[mcp]'
ticktick-mcp-cli doctor --json
ticktick-mcp-cli auth status --json
```

For Dida365 accounts, initialize the domestic profile before launching Claude Code:

```bash
ticktask auth init --service dida365 --client-id "$DIDA365_CLIENT_ID" --client-secret "$DIDA365_CLIENT_SECRET" --redirect-uri "http://localhost:8080/callback"
```

## Server definition

Use this stdio server definition in the Claude Code MCP configuration mechanism available in your installation:

```json
{
  "name": "ticktick",
  "command": "ticktick-mcp",
  "args": [],
  "env": {
    "TICKTASK_CONFIG_DIR": "${HOME}/.config/ticktask"
  }
}
```

If the runtime does not inherit your shell PATH, resolve and paste an absolute path:

```bash
which ticktick-mcp
```

## Smoke test prompt

Ask Claude Code:

```text
Use the ticktick MCP server to inspect available tools and list projects. Keep the check read-only.
```
