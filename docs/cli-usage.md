# CLI Usage

## Health and Auth

```bash
uv run ticktick-mcp-cli doctor --json
uv run ticktick-mcp-cli auth status --json
uv run ticktick-mcp-cli auth login --service ticktick --no-browser --json
uv run ticktick-mcp-cli auth login --service ticktick --callback-url 'http://localhost:8080/callback?code=***&state=STATE' --json
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
uv run ticktick-mcp-cli task analytics week --project Inbox --json
uv run ticktick-mcp-cli task add "Send invoice" --project Inbox --content "Include May details" --json
uv run ticktick-mcp-cli task get TASK_ID --project-id PROJECT_ID --json
uv run ticktick-mcp-cli task update TASK_ID --project-id PROJECT_ID --title "Send paid invoice" --json
uv run ticktick-mcp-cli task complete TASK_ID --project-id PROJECT_ID --yes --json
uv run ticktick-mcp-cli task delete TASK_ID --project-id PROJECT_ID --yes --json
uv run ticktick-mcp-cli task move TASK_ID --from-project-id PROJECT_ID --to-project-id OTHER_PROJECT_ID --json
uv run ticktick-mcp-cli task reminder set TASK_ID --project-id PROJECT_ID --reminder TRIGGER:PT10M --json
uv run ticktick-mcp-cli task reminder clear TASK_ID --project-id PROJECT_ID --json
uv run ticktick-mcp-cli task repeat set TASK_ID --project-id PROJECT_ID --preset weekly --json
uv run ticktick-mcp-cli task repeat set TASK_ID --project-id PROJECT_ID --rrule 'RRULE:FREQ=WEEKLY;BYDAY=MO' --json
uv run ticktick-mcp-cli task repeat clear TASK_ID --project-id PROJECT_ID --json
uv run ticktick-mcp-cli task batch complete --task-id TASK_ID_1 --task-id TASK_ID_2 --project-id PROJECT_ID --json
uv run ticktick-mcp-cli task batch delete --task-id TASK_ID --project-id PROJECT_ID --execute --yes --json
uv run ticktick-mcp-cli task batch move --task-id TASK_ID --from-project-id PROJECT_ID --to-project-id OTHER_PROJECT_ID --json
uv run ticktick-mcp-cli task tag add TASK_ID agent --project-id PROJECT_ID --json
uv run ticktick-mcp-cli task tag remove TASK_ID agent --project-id PROJECT_ID --json
uv run ticktick-mcp-cli task item add TASK_ID "Checklist item" --project-id PROJECT_ID --json
uv run ticktick-mcp-cli task item update TASK_ID ITEM_ID --project-id PROJECT_ID --title "Renamed" --status completed --json
uv run ticktick-mcp-cli task item complete TASK_ID ITEM_ID --project-id PROJECT_ID --json
uv run ticktick-mcp-cli task item delete TASK_ID ITEM_ID --project-id PROJECT_ID --yes --json
```

Batch commands default to dry-run previews; pass `--execute --yes` to mutate remote tasks. Reminder, repeat, and tag operations update the parent task through the official task update API and require exact task/project IDs. Repeat presets are `daily`, `weekly`, `monthly`, and `yearly`; `--rrule` also accepts raw RRULE strings. `task filter` uses the official `POST /open/v1/task/filter` endpoint; `task list --tag/--filter` applies deterministic local filtering over listed tasks. Smart filters: `today`, `overdue`, `upcoming`, `high-priority`, `no-date`.

Checklist item operations update the parent task through the official task update API, preserve `kind=CHECKLIST`, and require exact task/project/item IDs. Deleting a checklist item requires `--yes`.

Completed-task listing uses the official `POST /open/v1/task/completed` API. Global completed queries intentionally omit `projectIds`, which avoids missing completed Dida365 tasks.

`task analytics` combines open project data with completed-task range data and returns `summary`, `project_throughput`, `tag_distribution`, and `priority_distribution`. It accepts the same date presets as completed-task listing (`today`, `yesterday`, `week`) or explicit `--from/--to` dates. Global analytics also omits `projectIds` for the completed-task query for Dida365 completeness.

## Reports

```bash
uv run ticktick-mcp-cli report progress week --project Inbox --json
uv run ticktick-mcp-cli report progress --from 2026-05-01 --to 2026-05-17 --focus-type 1 --json
```

`report progress` derives a cross-domain scorecard from task analytics, habit check-ins, and focus sessions. It returns task completion/overdue rates, habit check-in counts, focus session duration, and a compact `scorecard` with `completed_tasks`, `habit_checkins`, `focus_minutes`, and `overdue_tasks`.

## Incremental sync/export state

```bash
uv run ticktick-mcp-cli sync state --json
uv run ticktick-mcp-cli sync mark tasks:all --timestamp 2026-05-01T00:00:00Z --json
uv run ticktick-mcp-cli sync export tasks --format jsonl --state-key tasks:all --status all --json
uv run ticktick-mcp-cli sync export tasks --format jsonl --state-key tasks:all --status all --save-state --json
```

The sync state file is stored next to the CLI config as `sync-state.json`. `sync export tasks` uses `--since` when supplied; otherwise it reads `last_synced_at` from `--state-key` and maps it to the task export `--from` date. `--save-state` records the current UTC timestamp after a successful export.

## Backups

```bash
uv run ticktick-mcp-cli backup tasks --output-dir ~/ticktask-backups --format markdown,jsonl,csv --status all --json
uv run ticktick-mcp-cli backup tasks --output-dir ~/ticktask-backups --date 2026-05-17 --project Inbox --from 2026-05-01 --to 2026-05-17 --json
```

`backup tasks` writes local files under `OUTPUT_DIR/YYYY-MM-DD/project-slug/` and creates a date-level `manifest.json` that records the formats, relative paths, byte sizes, filters, and task count. Supported backup formats are `json`, `jsonl`, `csv`, and `markdown`; the default is `markdown,jsonl,csv`.

## Habits

```bash
uv run ticktick-mcp-cli habit list --json
uv run ticktick-mcp-cli habit get HABIT_ID --json
uv run ticktick-mcp-cli habit create "Read" --goal 1 --unit time --json
uv run ticktick-mcp-cli habit update HABIT_ID --name "Read more" --json
uv run ticktick-mcp-cli habit checkin HABIT_ID 20260101 --value 1 --json
uv run ticktick-mcp-cli habit history HABIT_ID --from 20260101 --to 20260131 --json
```

Habit check-in stamps use integer `YYYYMMDD` format.

## Focus

```bash
uv run ticktick-mcp-cli focus list --from 2026-01-01 --to 2026-01-30 --type 0 --json
uv run ticktick-mcp-cli focus get FOCUS_ID --type 0 --json
uv run ticktick-mcp-cli focus delete FOCUS_ID --type 0 --yes --json
```

Focus type is `0` for Pomodoro and `1` for Timing. Focus list queries validate the official 30-day maximum range. Deleting a focus session requires `--yes`.

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
uv run ticktick-mcp-cli export focus --format csv --from 2026-01-01 --to 2026-01-30 --type 0
```

Supported formats are `json`, `jsonl`, `csv`, and `markdown`. Export commands emit raw export content instead of wrapping the output in the stable CLI result envelope. Focus exports include report-friendly `duration_seconds` and `duration_minutes` fields and use the same 30-day range validation as focus listing.

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

## Reliability and retries

The shared API client automatically retries read-only operations when the service returns `429` or transient `5xx` responses. If the service sends `Retry-After`, that delay is honored before the next attempt; otherwise the client uses bounded exponential backoff. Read-only `POST` endpoints such as task filters and completed-task range queries opt into the same retry behavior.

Mutating operations such as create/update/delete/complete/move do not blind-retry by default, because a network or server error may occur after the upstream service already applied the write. Error payloads include `details.status_code`, `details.path`, `details.retryable`, and, for rate limits, `details.retry_after` so agents can choose a safe recovery plan.



