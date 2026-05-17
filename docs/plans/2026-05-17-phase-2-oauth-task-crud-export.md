# Ticktask Phase 2 OAuth + Task CRUD + Export Implementation Plan

> **For Hermes:** User asked to continue the plan → Codex implementation → Hermes review workflow. Use Codex CLI to implement this plan, then verify independently.

**Goal:** Move ticktask from a working architecture MVP to a daily-usable CLI/MCP tool by adding OAuth login/refresh, full task CRUD/move/delete, completed-task query commands, and export formats.

**Architecture:** Keep `src/ticktask/core/` as the only domain/API layer. CLI and MCP remain thin frontends. OAuth/token refresh, HTTP endpoints, task operations, and export serialization must be implemented once in core and reused by both CLI and MCP.

**Tech Stack:** Python 3.11+, Typer, httpx, pydantic-free dataclasses already present, Rich, pytest, optional MCP SDK.

---

## Non-Negotiable Constraints

1. Do not commit real credentials, access tokens, refresh tokens, or user-local config.
2. Preserve service profiles:
   - `ticktick`: `https://api.ticktick.com`
   - `dida365`: `https://api.dida365.com`
3. Use official completed task endpoint: `POST /open/v1/task/completed`.
4. For global completed queries, do **not** include `projectIds` in the request body; this avoids the known Dida365 missing-data pitfall.
5. All machine-facing CLI commands must support stable JSON success/error shape.
6. MCP public tool signatures must expose only JSON-schema-compatible parameters.
7. Destructive operations (`delete`, `complete`, bulk actions) require explicit confirmation (`--yes` or MCP `yes=true`).
8. Prefer TDD: add or update tests before implementation.

## New User-Facing Features

### OAuth

- `ticktask auth login [--service SERVICE] [--no-browser] [--json]`
- `ticktask auth refresh [--service SERVICE] [--json]`
- AuthManager should support:
  - authorization URL construction;
  - local callback server for `redirect_uri` host/port;
  - code exchange against `/oauth/token` or configurable token path;
  - refresh token flow;
  - token expiry tracking when API returns `expires_in`.

Notes:
- No hosted OAuth broker.
- Users provide their own `client_id` and `client_secret` via `auth init`.
- Tests must mock HTTP and local callback behaviors; do not open real browser in tests.

### Task CRUD + move/delete

CLI:

- `ticktask task get TASK_ID --project-id PROJECT_ID [--json]`
- `ticktask task update TASK_ID --project-id PROJECT_ID [--title TITLE] [--content TEXT] [--due DATE] [--priority PRIORITY] [--json]`
- `ticktask task delete TASK_ID --project-id PROJECT_ID --yes [--json]`
- `ticktask task move TASK_ID --from-project-id ID --to-project-id ID [--json]`
- Preserve existing:
  - `task list`
  - `task search`
  - `task add`
  - `task complete`
  - aliases `add`, `done`, `today`

Core client endpoints:

- `GET /open/v1/project/{projectId}/task/{taskId}`
- `POST /open/v1/task/{taskId}`
- `DELETE /open/v1/project/{projectId}/task/{taskId}`
- `POST /open/v1/task/move`

### Completed commands

CLI:

- `ticktask completed [today|yesterday|week] [--from DATE] [--to DATE] [--project PROJECT] [--json]`
- `ticktask task list --status completed [--from DATE] [--to DATE] [--project PROJECT] [--json]`

Core:

- Add a date parsing helper for `today`, `yesterday`, `week`, explicit `YYYY-MM-DD`.
- Completed query should use broad safe defaults only when user does not specify a range.

### Export

CLI:

- `ticktask export tasks --format json|jsonl|csv|markdown [--project PROJECT] [--status open|completed|all] [--from DATE] [--to DATE]`
- `ticktask export completed --format json|jsonl|csv|markdown [--from DATE] [--to DATE]`

Core:

- Add serializer functions in `src/ticktask/core/exporters.py`.
- JSON export can reuse stable payload; jsonl/csv/markdown should be deterministic and test-covered.

### MCP tools

Add tools corresponding to new capabilities:

- `ticktask_get_task`
- `ticktask_update_task`
- `ticktask_delete_task`
- `ticktask_move_task`
- `ticktask_completed`
- `ticktask_export_tasks`

Each tool returns the same result/error model and uses core services.

## Implementation Tasks

### Task 1: Date range parsing

**Objective:** Add deterministic parsing for completed/export ranges.

**Files:**
- Create: `src/ticktask/core/dates.py`
- Test: `tests/core/test_dates.py`

**Acceptance:**
- `today`, `yesterday`, `week`, and explicit `YYYY-MM-DD` parse into start/end strings.
- Invalid dates return structured errors through service/CLI paths.

### Task 2: OAuth login and refresh

**Objective:** Implement actual OAuth local authorization code flow and refresh flow in core + CLI.

**Files:**
- Modify: `src/ticktask/core/auth.py`
- Modify: `src/ticktask/core/client.py` if token exchange helpers belong there
- Modify: `src/ticktask/cli/auth.py`
- Test: `tests/core/test_auth.py`, `tests/cli/test_auth_cli.py`

**Acceptance:**
- Auth URL includes `client_id`, `redirect_uri`, `response_type=code`, and `scope` if configured.
- Token exchange and refresh are HTTP-mocked.
- `auth login --no-browser` can print URL and wait for/accept a callback code in a testable way.
- `auth refresh --json` updates stored access token and expiry.

### Task 3: Task CRUD client/service

**Objective:** Add get/update/delete/move methods to client and service.

**Files:**
- Modify: `src/ticktask/core/client.py`
- Modify: `src/ticktask/core/services.py`
- Modify: `src/ticktask/core/models.py` if needed
- Test: `tests/core/test_client.py`, `tests/core/test_services.py`

**Acceptance:**
- Correct HTTP method/path/body for get/update/delete/move.
- Delete requires confirmation in service.
- Move uses POST `/open/v1/task/move` with array body even for one task.

### Task 4: Task CLI commands

**Objective:** Expose task CRUD/move/delete and completed date range options.

**Files:**
- Modify: `src/ticktask/cli/task.py`
- Modify: `src/ticktask/cli/app.py`
- Test: `tests/cli/test_task_cli.py`

**Acceptance:**
- Commands listed above parse and call services.
- JSON success/error shape is stable.
- Delete without `--yes` returns confirmation error.

### Task 5: Completed command

**Objective:** Add top-level completed command for human and Agent use.

**Files:**
- Modify: `src/ticktask/cli/app.py`
- Test: `tests/cli/test_task_cli.py` or new `tests/cli/test_completed_cli.py`

**Acceptance:**
- `ticktask completed today --json` works under mocked service.
- `--from/--to` supported.

### Task 6: Export serializers and CLI

**Objective:** Add deterministic export output for tasks/completed.

**Files:**
- Create: `src/ticktask/core/exporters.py`
- Create: `src/ticktask/cli/export.py`
- Modify: `src/ticktask/cli/app.py`
- Test: `tests/core/test_exporters.py`, `tests/cli/test_export_cli.py`

**Acceptance:**
- json/jsonl/csv/markdown outputs are tested.
- Export commands do not wrap output in Rich formatting unless `--format` is human markdown.

### Task 7: MCP expanded tools

**Objective:** Expose new task/completed/export capabilities to MCP.

**Files:**
- Modify: `src/ticktask/mcp/tools.py`
- Modify: `src/ticktask/mcp/server.py`
- Test: `tests/mcp/test_tools.py`

**Acceptance:**
- `build_server()` succeeds with optional MCP installed.
- Public MCP signatures remain JSON-schema-compatible.
- Delete requires `yes=true`.

### Task 8: Docs update

**Objective:** Update README/docs to reflect phase 2 features.

**Files:**
- Modify: `README.md`
- Modify: `docs/oauth.md`
- Modify: `docs/cli-usage.md`
- Modify: `docs/mcp-usage.md`
- Modify: `docs/agent-usage.md`

**Acceptance:**
- Docs show OAuth login/refresh, task CRUD, completed, export, MCP config.
- Docs mention no bundled OAuth client secret.

## Verification Commands

Run before completion:

```bash
uv run pytest -q
uv run ticktask --help >/tmp/ticktask-help.txt
uv run tt --help >/tmp/tt-help.txt
uv run ticktask doctor --json
uv run ticktask auth status --json
uv run --with 'mcp>=1.0' python -c 'from ticktask.mcp.server import build_server; build_server(); print("mcp_build_ok")'
```

## Hermes Review Checklist

- [ ] Shared core still owns business logic.
- [ ] No credentials committed.
- [ ] OAuth code is testable and mocked.
- [ ] Completed task endpoint remains `POST /open/v1/task/completed`.
- [ ] Global completed query omits `projectIds`.
- [ ] Destructive operations require confirmation.
- [ ] MCP schema build passes.
- [ ] Tests pass.
- [ ] Docs match implemented commands.
