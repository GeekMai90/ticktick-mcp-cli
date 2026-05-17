# MCP Usage

Install the optional MCP dependency:

```bash
uv sync --extra mcp
```

Run the stdio server:

```bash
uv run ticktick-mcp
```

Example MCP client command config:

```json
{
  "mcpServers": {
    "ticktask": {
      "command": "uv",
      "args": ["run", "ticktick-mcp"],
      "cwd": "/path/to/ticktick-mcp-cli"
    }
  }
}
```

Tools:

- `ticktask_doctor`
- `ticktask_auth_status`
- `ticktask_list_projects`
- `ticktask_create_project`
- `ticktask_update_project`
- `ticktask_delete_project`
- `ticktask_list_tasks`
- `ticktask_search_tasks`
- `ticktask_create_task`
- `ticktask_complete_task`
- `ticktask_today`
- `ticktask_get_task`
- `ticktask_update_task`
- `ticktask_delete_task`
- `ticktask_move_task`
- `ticktask_completed`
- `ticktask_export_tasks`

Tool functions are importable from `ticktask.mcp.tools` for unit testing without launching stdio.

Destructive MCP tools require explicit confirmation. For example, `ticktask_delete_task` and `ticktask_delete_project` return `CONFIRMATION_REQUIRED` unless `yes=true`.
