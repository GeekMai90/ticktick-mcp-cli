# OpenClaw MCP Config

OpenClaw can use TickTick MCP CLI as a stdio MCP server for task and project automation.

## Prerequisites

```bash
uv tool install 'ticktick-mcp-cli[mcp]'
ticktick-mcp-cli doctor --json
ticktick-mcp-cli auth status --json
```

For Dida365, configure the domestic service profile first:

```bash
ticktask auth init --service dida365 --client-id "$DIDA365_CLIENT_ID" --client-secret "$DIDA365_CLIENT_SECRET" --redirect-uri "http://localhost:8080/callback"
```

## Server definition

Use this stdio server entry in your OpenClaw MCP server configuration:

```json
{
  "name": "ticktick",
  "transport": "stdio",
  "command": "ticktick-mcp",
  "args": [],
  "env": {
    "TICKTASK_CONFIG_DIR": "${HOME}/.config/ticktask"
  }
}
```

When OpenClaw runs as a service and cannot resolve PATH, replace the command with:

```bash
which ticktick-mcp
```

## Smoke test prompt

Ask OpenClaw:

```text
Call ticktask_describe_tools from the ticktick MCP server, then list projects. This smoke test is read-only.
```
