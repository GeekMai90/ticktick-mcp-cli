# ticktask

Agent-friendly CLI and MCP server for TickTick international and Dida365 domestic APIs.

`ticktask` keeps API behavior in one shared Python core under `src/ticktask/core/`.
The CLI and MCP server are thin frontends over that core, so humans and agents get the
same service profiles, auth handling, safety checks, and JSON result shapes.

## Install

```bash
uv sync
uv run ticktask --help
uv run tt --help
```

Console scripts:

- `ticktask = ticktask.cli.app:app`
- `tt = ticktask.cli.app:app`
- `ticktask-mcp = ticktask.mcp.server:main`

## Service Profiles

- `ticktick` -> `https://api.ticktick.com`
- `dida365` -> `https://api.dida365.com`

Configure OAuth app credentials locally:

```bash
uv run ticktask auth init \
  --service ticktick \
  --client-id "$TICKTICK_CLIENT_ID" \
  --client-secret "$TICKTICK_CLIENT_SECRET" \
  --redirect-uri "http://localhost:8080/callback"
```

For mocked/local testing only, you can also persist an existing token:

```bash
uv run ticktask auth init \
  --service dida365 \
  --client-id "$DIDA_CLIENT_ID" \
  --client-secret "$DIDA_CLIENT_SECRET" \
  --redirect-uri "http://localhost:8080/callback" \
  --access-token "$DIDA_ACCESS_TOKEN"
```

Do not commit config files, client secrets, access tokens, or refresh tokens.

## CLI

Human-readable commands:

```bash
uv run ticktask doctor
uv run ticktask config path
uv run ticktask auth status
uv run ticktask auth login --no-browser
uv run ticktask auth refresh
uv run ticktask project list
uv run ticktask task list
uv run ticktask task get TASK_ID --project-id PROJECT_ID
uv run ticktask today
uv run ticktask add "Plan release"
```

Agent-safe JSON commands:

```bash
uv run ticktask doctor --json
uv run ticktask auth status --json
uv run ticktask project list --json
uv run ticktask task list --json
uv run ticktask task list --status completed --from 2026-05-01 --to 2026-05-17 --json
uv run ticktask task search "release" --json
uv run ticktask task add "Plan release" --project Inbox --json
uv run ticktask task update TASK_ID --project-id PROJECT_ID --title "New title" --json
uv run ticktask task complete TASK_ID --project-id PROJECT_ID --yes --json
uv run ticktask task delete TASK_ID --project-id PROJECT_ID --yes --json
uv run ticktask task move TASK_ID --from-project-id PROJECT_ID --to-project-id OTHER_PROJECT_ID --json
uv run ticktask done TASK_ID --project-id PROJECT_ID --yes --json
uv run ticktask completed today --json
uv run ticktask export tasks --format jsonl --status all
uv run ticktask export completed --format markdown --from 2026-05-01 --to 2026-05-17
```

All machine-facing successes use:

```json
{"ok": true, "data": {}, "meta": {}}
```

All machine-facing errors use:

```json
{"ok": false, "error": {"code": "ERROR_CODE", "message": "Human message", "hint": "Next step"}}
```

Dangerous operations require exact IDs and explicit confirmation. For example,
task completion requires `--project-id PROJECT_ID --yes`.

Completed-task listing uses the official `POST /open/v1/task/completed` API. Global completed queries intentionally omit `projectIds`, which avoids missing completed Dida365 tasks.

## MCP

Install optional MCP support, then run stdio:

```bash
uv sync --extra mcp
uv run ticktask-mcp
```

If the optional `mcp` package is unavailable, `ticktask-mcp` exits with a clear install hint.

MCP tools:

- `ticktask_doctor`
- `ticktask_auth_status`
- `ticktask_list_projects`
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

## Docs

- [Installation](docs/installation.md)
- [OAuth](docs/oauth.md)
- [CLI Usage](docs/cli-usage.md)
- [MCP Usage](docs/mcp-usage.md)
- [Agent Usage](docs/agent-usage.md)
- [Implementation Plan](docs/plans/2026-05-17-ticktask-cli-mcp-plan.md)
