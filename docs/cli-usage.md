# CLI Usage

## Health and Auth

```bash
uv run ticktask doctor --json
uv run ticktask auth status --json
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
uv run ticktask task search "invoice" --json
uv run ticktask task add "Send invoice" --project Inbox --content "Include May details" --json
uv run ticktask task complete TASK_ID --project-id PROJECT_ID --yes --json
```

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
