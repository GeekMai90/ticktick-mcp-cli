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

- `ticktask_describe_tools`
- `ticktask_cli_parity`
- `ticktask_doctor`
- `ticktask_auth_status`
- `ticktask_list_projects`
- `ticktask_create_project`
- `ticktask_update_project`
- `ticktask_delete_project`
- `ticktask_list_tasks`
- `ticktask_filter_tasks`
- `ticktask_search_tasks`
- `ticktask_create_task`
- `ticktask_complete_task`
- `ticktask_today`
- `ticktask_get_task`
- `ticktask_update_task`
- `ticktask_delete_task`
- `ticktask_move_task`
- `ticktask_add_task_tag`
- `ticktask_remove_task_tag`
- `ticktask_add_checklist_item`
- `ticktask_update_checklist_item`
- `ticktask_complete_checklist_item`
- `ticktask_delete_checklist_item`
- `ticktask_completed`
- `ticktask_export_tasks`

`ticktask_describe_tools` returns agent-facing metadata for every MCP tool: descriptions, CLI parity, parameters, enum constraints, examples, destructive-operation flags, and confirmation requirements. `ticktask_cli_parity` returns the same mapping as rows for audits and planning.

`ticktask_list_tasks` accepts optional `tag` and `filter_preset` arguments. `ticktask_filter_tasks` uses the Open API filter endpoint for deterministic tag/priority/date filtering. Tag mutation tools update the parent task tags through the official task update API.

Tool functions are importable from `ticktask.mcp.tools` for unit testing without launching stdio.

Destructive MCP tools require explicit confirmation. For example, `ticktask_delete_task`, `ticktask_delete_project`, and `ticktask_delete_checklist_item` return `CONFIRMATION_REQUIRED` unless `yes=true`.


Example metadata call:

```python
from ticktask.mcp import tools

definitions = tools.ticktask_describe_tools()["data"]
print(definitions["ticktask_list_tasks"]["parameters"]["status"]["enum"])
print(definitions["ticktask_delete_task"]["confirmation_required"])
```
