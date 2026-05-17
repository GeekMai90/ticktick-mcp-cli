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
- `ticktask_diagnostic_bundle`
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
- `ticktask_task_analytics`
- `ticktask_progress_report`
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
- `ticktask_sync_state`
- `ticktask_mark_sync_state`
- `ticktask_sync_export_tasks`
- `ticktask_backup_tasks`
- `ticktask_export_focuses`

`ticktask_describe_tools` returns agent-facing metadata for every MCP tool: descriptions, CLI parity, parameters, enum constraints, examples, destructive-operation flags, and confirmation requirements. `ticktask_cli_parity` returns the same mapping as rows for audits and planning. `ticktask_diagnostic_bundle(output_path="ticktask-diagnostics.zip")` writes the same redacted support ZIP as `ticktask doctor bundle`.

Resources:

- `ticktask://projects` — read-only project list for planning and exact-ID lookup.
- `ticktask://config` — sanitized active service/profile configuration with secret fields redacted to boolean `*_configured` flags.
- `ticktask://saved-views` — built-in smart-filter presets (`today`, `overdue`, `upcoming`, `high-priority`, `no-date`) with equivalent MCP tool arguments and CLI commands.

Resource functions are importable from `ticktask.mcp.resources` for unit testing without launching stdio.

Prompts:

- `ticktask_daily_planning(project=None, include_overdue=True)` — plan today using `ticktask://projects`, `ticktask://saved-views`, and safe task tools.
- `ticktask_weekly_review(project=None, period="week")` — review progress using `ticktask_progress_report`, `ticktask_task_analytics`, and `ticktask_completed`.
- `ticktask_cleanup(project=None, older_than_days=30)` — find stale cleanup candidates and require dry-run batch previews before any confirmed mutation.
- `ticktask_export(project=None, output_format="markdown", output_dir="~/ticktask-backups")` — choose immediate export, local backup, or incremental sync.

Prompt functions are importable from `ticktask.mcp.prompts` for unit testing without launching stdio.

Task date and enum inputs are normalized before the shared core reaches the API: task due/filter dates accept `YYYY-MM-DD`, `today`, `tomorrow`, and `next <weekday>`; priorities accept aliases such as `p1`/`p2`/`p3`; statuses accept aliases such as `done`; project kind/view-mode inputs are validated.

`ticktask_list_tasks` accepts optional `tag` and `filter_preset` arguments. `ticktask_filter_tasks` uses the Open API filter endpoint for deterministic tag/priority/date filtering. `ticktask_task_analytics` returns open/completed/overdue counts, project throughput, tag distribution, and priority distribution for a preset or explicit date range. `ticktask_progress_report` combines task analytics, habit check-ins, and focus duration into one cross-domain scorecard. `ticktask_sync_state`, `ticktask_mark_sync_state`, and `ticktask_sync_export_tasks` provide checkpointed incremental task exports backed by the local `sync-state.json` file. `ticktask_backup_tasks` writes local date/project backup files in Markdown, JSONL, CSV, or JSON and returns a manifest path. Batch tools default to `dry_run=true`; pass `dry_run=false` and `yes=true` to execute. Reminder, repeat, and tag mutation tools update the parent task through the official task update API. Habit tools cover list/get/create/update, check-in, and history. Focus tools cover list/get/delete plus report-friendly exports, and enforce the official 30-day query window.

Tool functions are importable from `ticktask.mcp.tools` for unit testing without launching stdio.

Destructive MCP tools require explicit confirmation. For example, `ticktask_delete_task`, `ticktask_delete_project`, `ticktask_delete_checklist_item`, and `ticktask_delete_focus` return `CONFIRMATION_REQUIRED` unless `yes=true`.

MCP tools use the same reliability behavior as the CLI because both frontends call the shared core client. Read-only operations retry `429` and transient `5xx` responses with `Retry-After`/bounded backoff. Mutating writes do not blind-retry, and API errors include retry details (`status_code`, `path`, `retryable`, and optional `retry_after`) for agent recovery logic. All MCP error payloads also include structured `category`, `retryable`, and `remediation` fields; agents should use `remediation.safe_to_retry` before retrying failed tool calls.


Example metadata call:

```python
from ticktask.mcp import tools

definitions = tools.ticktask_describe_tools()["data"]
print(definitions["ticktask_list_tasks"]["parameters"]["status"]["enum"])
print(definitions["ticktask_delete_task"]["confirmation_required"])
```



