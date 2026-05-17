# Hermes MCP Config

Hermes can run TickTick MCP CLI as a stdio MCP server and expose its tools to the agent.

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

## Hermes config snippet

Add a server entry similar to this in your Hermes config:

```yaml
mcp_servers:
  ticktick:
    command: ticktick-mcp
    args: []
    env:
      TICKTASK_CONFIG_DIR: ${HOME}/.config/ticktask
```

If Hermes runs without your login shell PATH, use an absolute command path:

```bash
which ticktick-mcp
```

## Agent smoke test

Ask Hermes:

```text
Use the ticktick MCP tools to call ticktask_describe_tools and list projects. This is read-only; do not mutate tasks.
```

Expected behavior: Hermes sees the same capabilities as the human CLI, backed by the shared core service.
