# Cursor MCP Config

Cursor can connect to TickTick MCP CLI through a project or user MCP JSON config.

## Prerequisites

```bash
uv tool install 'ticktick-mcp-cli[mcp]'
ticktick-mcp-cli doctor --json
ticktick-mcp-cli auth status --json
```

Use Dida365 by configuring the service profile before Cursor starts:

```bash
ticktask auth init --service dida365 --client-id "$DIDA365_CLIENT_ID" --client-secret "$DIDA365_CLIENT_SECRET" --redirect-uri "http://localhost:8080/callback"
```

## Config snippet

Add a server like this to Cursor's MCP configuration:

```json
{
  "mcpServers": {
    "ticktick": {
      "command": "ticktick-mcp",
      "args": [],
      "env": {
        "TICKTASK_CONFIG_DIR": "${HOME}/.config/ticktask"
      }
    }
  }
}
```

If Cursor cannot find `ticktick-mcp`, replace it with the absolute executable path:

```bash
which ticktick-mcp
```

## Smoke test prompt

Ask Cursor Agent:

```text
Use the ticktick MCP server to show tool metadata and list projects only. Do not perform write operations.
```
