# Claude Desktop MCP Config

Claude Desktop can launch TickTick MCP CLI as a local stdio MCP server.

## Prerequisites

```bash
uv tool install 'ticktick-mcp-cli[mcp]'
ticktick-mcp-cli doctor --json
ticktick-mcp-cli auth status --json
```

For Dida365, initialize or select the domestic profile before using Claude Desktop:

```bash
ticktask auth init --service dida365 --client-id "$DIDA365_CLIENT_ID" --client-secret "$DIDA365_CLIENT_SECRET" --redirect-uri "http://localhost:8080/callback"
```

## Config snippet

Add this to Claude Desktop's MCP config file, then restart Claude Desktop:

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

If your shell cannot resolve tool-installed executables inside GUI apps, replace `"ticktick-mcp"` with the absolute path from:

```bash
which ticktick-mcp
```

## Smoke test prompt

Ask Claude:

```text
Use the ticktick MCP server to describe available tools, then list projects. Do not create, update, complete, move, or delete anything.
```
