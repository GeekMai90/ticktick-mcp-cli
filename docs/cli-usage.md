# CLI Usage

## Health and Auth

```bash
uv run ticktask doctor --json
uv run ticktask auth status --json
uv run ticktask auth login --service ticktick --no-browser --json
uv run ticktask auth login --service ticktick --callback-url 'http://localhost:8080/callback?code=CALLBACK_CODE&state=STATE' --json
uv run ticktask auth login --service ticktick --code CALLBACK_CODE --state STATE --json
uv run ticktask auth refresh --service ticktick --json
uv run ticktask config path
```

## Projects

```bash
uv run ticktask project list --json
uv run ticktask project get PROJECT_ID --json
uv run ticktask project data PROJECT_ID --json
```

## Tasks

```bash
uv run ticktask task list --json
uv run ticktask task list --project Inbox --status open --json
uv run ticktask task list --status completed --from 2026-05-01 --to 2026-05-17 --json
uv run ticktask task search "invoice" --json
uv run ticktask task add "Send invoice" --project Inbox --content "Include May details" --json
uv run ticktask task get TASK_ID --project-id PROJECT_ID --json
uv run ticktask task update TASK_ID --project-id PROJECT_ID --title "Send paid invoice" --json
uv run ticktask task complete TASK_ID --project-id PROJECT_ID --yes --json
uv run ticktask task delete TASK_ID --project-id PROJECT_ID --yes --json
uv run ticktask task move TASK_ID --from-project-id PROJECT_ID --to-project-id OTHER_PROJECT_ID --json
```

Completed-task listing uses the official `POST /open/v1/task/completed` API. Global completed queries intentionally omit `projectIds`, which avoids missing completed Dida365 tasks.

## Completed

```bash
uv run ticktask completed today --json
uv run ticktask completed yesterday --json
uv run ticktask completed week --json
uv run ticktask completed --from 2026-05-01 --to 2026-05-17 --project Inbox --json
```

## Export

```bash
uv run ticktask export tasks --format json --status open
uv run ticktask export tasks --format jsonl --status all --from 2026-05-01 --to 2026-05-17
uv run ticktask export tasks --format csv --project Inbox
uv run ticktask export completed --format markdown --from 2026-05-01 --to 2026-05-17
```

Supported formats are `json`, `jsonl`, `csv`, and `markdown`. Export commands emit raw export content instead of wrapping the output in the stable CLI result envelope.

Aliases:

```bash
uv run ticktask today --json
uv run ticktask add "Send invoice" --json
uv run ticktask done TASK_ID --project-id PROJECT_ID --yes --json
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
