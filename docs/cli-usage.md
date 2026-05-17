# CLI Usage

## Health and Auth

```bash
uv run ticktick-mcp-cli doctor --json
uv run ticktick-mcp-cli auth status --json
uv run ticktick-mcp-cli auth login --service ticktick --no-browser --json
uv run ticktick-mcp-cli auth login --service ticktick --callback-url 'http://localhost:8080/callback?code=CALLBACK_CODE&state=STATE' --json
uv run ticktick-mcp-cli auth login --service ticktick --code CALLBACK_CODE --state STATE --json
uv run ticktick-mcp-cli auth refresh --service ticktick --json
uv run ticktick-mcp-cli config path
uv run ticktick-mcp-cli integration smoke --json
```

## Projects

```bash
uv run ticktick-mcp-cli project list --json
uv run ticktick-mcp-cli project get PROJECT_ID --json
uv run ticktick-mcp-cli project data PROJECT_ID --json
uv run ticktick-mcp-cli project create "Focus" --color "#00aa00" --view-mode list --json
uv run ticktick-mcp-cli project update PROJECT_ID --name "Renamed" --closed --json
uv run ticktick-mcp-cli project delete PROJECT_ID --yes --json
```

## Tasks

```bash
uv run ticktick-mcp-cli task list --json
uv run ticktick-mcp-cli task list --project Inbox --status open --json
uv run ticktick-mcp-cli task list --status completed --from 2026-05-01 --to 2026-05-17 --json
uv run ticktick-mcp-cli task list --tag agent --filter high-priority --json
uv run ticktick-mcp-cli task filter --tag agent --project Inbox --priority high --json
uv run ticktick-mcp-cli task search "invoice" --json
uv run ticktick-mcp-cli task add "Send invoice" --project Inbox --content "Include May details" --json
uv run ticktick-mcp-cli task get TASK_ID --project-id PROJECT_ID --json
uv run ticktick-mcp-cli task update TASK_ID --project-id PROJECT_ID --title "Send paid invoice" --json
uv run ticktick-mcp-cli task complete TASK_ID --project-id PROJECT_ID --yes --json
uv run ticktick-mcp-cli task delete TASK_ID --project-id PROJECT_ID --yes --json
uv run ticktick-mcp-cli task move TASK_ID --from-project-id PROJECT_ID --to-project-id OTHER_PROJECT_ID --json
uv run ticktick-mcp-cli task tag add TASK_ID agent --project-id PROJECT_ID --json
uv run ticktick-mcp-cli task tag remove TASK_ID agent --project-id PROJECT_ID --json
uv run ticktick-mcp-cli task item add TASK_ID "Checklist item" --project-id PROJECT_ID --json
uv run ticktick-mcp-cli task item update TASK_ID ITEM_ID --project-id PROJECT_ID --title "Renamed" --status completed --json
uv run ticktick-mcp-cli task item complete TASK_ID ITEM_ID --project-id PROJECT_ID --json
uv run ticktick-mcp-cli task item delete TASK_ID ITEM_ID --project-id PROJECT_ID --yes --json
```

Tag operations update the parent task through the official task update API and require exact task/project IDs. `task filter` uses the official `POST /open/v1/task/filter` endpoint; `task list --tag/--filter` applies deterministic local filtering over listed tasks. Smart filters: `today`, `overdue`, `upcoming`, `high-priority`, `no-date`.

Checklist item operations update the parent task through the official task update API, preserve `kind=CHECKLIST`, and require exact task/project/item IDs. Deleting a checklist item requires `--yes`.

Completed-task listing uses the official `POST /open/v1/task/completed` API. Global completed queries intentionally omit `projectIds`, which avoids missing completed Dida365 tasks.

## Completed

```bash
uv run ticktick-mcp-cli completed today --json
uv run ticktick-mcp-cli completed yesterday --json
uv run ticktick-mcp-cli completed week --json
uv run ticktick-mcp-cli completed --from 2026-05-01 --to 2026-05-17 --project Inbox --json
```

## Export

```bash
uv run ticktick-mcp-cli export tasks --format json --status open
uv run ticktick-mcp-cli export tasks --format jsonl --status all --from 2026-05-01 --to 2026-05-17
uv run ticktick-mcp-cli export tasks --format csv --project Inbox
uv run ticktick-mcp-cli export completed --format markdown --from 2026-05-01 --to 2026-05-17
```

Supported formats are `json`, `jsonl`, `csv`, and `markdown`. Export commands emit raw export content instead of wrapping the output in the stable CLI result envelope.

Aliases:

```bash
uv run ticktick-mcp-cli today --json
uv run ticktick-mcp-cli add "Send invoice" --json
uv run ticktick-mcp-cli done TASK_ID --project-id PROJECT_ID --yes --json
```

## JSON Contract

Success:

```json
{"ok": true, "data": {}, "meta": {}}
```

Error:

```json
{"ok": false, "error": {"code": "ERROR_CODE", "message": "Human message", "hint": "Next step"}}
```

Agents should branch on `ok`, then on `error.code`.
