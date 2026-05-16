# MCP Usage

Install the optional MCP dependency:

```bash
uv sync --extra mcp
```

Run the stdio server:

```bash
uv run ticktask-mcp
```

Example MCP client command config:

```json
{
  "mcpServers": {
    "ticktask": {
      "command": "uv",
      "args": ["run", "ticktask-mcp"],
      "cwd": "/path/to/ticktask"
    }
  }
}
```

Tools:

- `ticktask_doctor`
- `ticktask_auth_status`
- `ticktask_list_projects`
- `ticktask_list_tasks`
- `ticktask_search_tasks`
- `ticktask_create_task`
- `ticktask_complete_task`
- `ticktask_today`

Tool functions are importable from `ticktask.mcp.tools` for unit testing without launching stdio.
