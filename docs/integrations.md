# MCP Integration Examples

This page links copy-pasteable MCP server configuration examples for agent runtimes that can call TickTick MCP CLI through stdio.

## Install first

Install the CLI and MCP server extra:

```bash
uv tool install 'ticktick-mcp-cli[mcp]'
# or
pipx install 'ticktick-mcp-cli[mcp]'
```

Verify local auth and config before wiring an agent runtime:

```bash
ticktick-mcp-cli doctor --json
ticktick-mcp-cli auth status --json
```

If you need isolated credentials for a runtime, set `TICKTASK_CONFIG_DIR` to a runtime-specific config directory. The examples use Dida365/TickTick profile data already configured by the CLI; use `ticktask auth init --service dida365 ...` when you want the domestic Dida365 API.

## Runtime guides

- [Claude Desktop](integrations/claude-desktop.md)
- [Hermes](integrations/hermes.md)
- [Cursor](integrations/cursor.md)
- [Claude Code](integrations/claude-code.md)
- [OpenClaw](integrations/openclaw.md)

## Common stdio command

All runtimes eventually launch the same stdio server:

```bash
ticktick-mcp
```

Legacy alias:

```bash
ticktask-mcp
```

Prefer `ticktick-mcp` for new configs.
