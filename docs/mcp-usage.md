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
- `ticktask_batch_complete_tasks`
- `ticktask_batch_delete_tasks`
- `ticktask_batch_move_tasks`
- `ticktask_set_task_reminders`
- `ticktask_clear_task_reminders`
- `ticktask_set_task_repeat`
- `ticktask_clear_task_repeat`
- `ticktask_add_task_tag`
- `ticktask_remove_task_tag`
- `ticktask_add_checklist_item`
- `ticktask_update_checklist_item`
- `ticktask_complete_checklist_item`
- `ticktask_delete_checklist_item`
- `ticktask_completed`
- `ticktask_list_habits`
- `ticktask_get_habit`
- `ticktask_create_habit`
- `ticktask_update_habit`
- `ticktask_checkin_habit`
- `ticktask_habit_checkins`
- `ticktask_list_focuses`
- `ticktask_get_focus`
- `ticktask_delete_focus`
- `ticktask_export_tasks`
- `ticktask_export_focuses`

`ticktask_describe_tools` returns agent-facing metadata for every MCP tool: descriptions, CLI parity, parameters, enum constraints, examples, destructive-operation flags, and confirmation requirements. `ticktask_cli_parity` returns the same mapping as rows for audits and planning.

`ticktask_list_tasks` accepts optional `tag` and `filter_preset` arguments. `ticktask_filter_tasks` uses the Open API filter endpoint for deterministic tag/priority/date filtering. Batch tools default to `dry_run=true`; pass `dry_run=false` and `yes=true` to execute. Reminder, repeat, and tag mutation tools update the parent task through the official task update API. Habit tools cover list/get/create/update, check-in, and history. Focus tools cover list/get/delete plus report-friendly exports, and enforce the official 30-day list/export range limit.

Tool functions are importable from `ticktask.mcp.tools` for unit testing without launching stdio.

Destructive MCP tools require explicit confirmation. For example, `ticktask_delete_task`, `ticktask_delete_project`, `ticktask_delete_checklist_item`, and `ticktask_delete_focus` return `CONFIRMATION_REQUIRED` unless `yes=true`.


Example metadata call:

```python
from ticktask.mcp import tools

definitions = tools.ticktask_describe_tools()["data"]
print(definitions["ticktask_list_tasks"]["parameters"]["status"]["enum"])
print(definitions["ticktask_delete_task"]["confirmation_required"])
```



