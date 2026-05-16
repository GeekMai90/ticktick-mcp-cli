# Ticktask CLI + MCP Implementation Plan

> **For Hermes:** User requested division of labor: Hermes plans, Codex implements, Hermes reviews. Use Codex CLI for implementation, then verify with tests and source inspection.

**Goal:** Build `ticktask`, an open-source, agent-friendly CLI and MCP server for TickTick international and Dida365 domestic APIs.

**Architecture:** One shared Python core library handles service profiles, config, auth/token storage, HTTP client, domain services, errors, and date parsing. The CLI (`tt`/`ticktask`) and MCP server (`ticktask-mcp` or `ticktask mcp`) are thin frontends over that shared core. All machine-facing outputs use stable JSON/error shapes.

**Tech Stack:** Python 3.11+, Typer, httpx, pydantic, rich, keyring optional, mcp Python SDK optional, pytest, respx/pytest-httpx.

---

## Product Principles

1. **Agent-friendly first-class support:** every command supports `--json`; errors have stable codes; destructive operations require explicit confirmation in non-interactive contexts.
2. **Human-friendly CLI:** default output should be readable with Rich; short aliases should exist for common actions.
3. **One core, two frontends:** CLI and MCP must not duplicate API behavior.
4. **TickTick + Dida365:** service profiles must support both `https://api.ticktick.com` and `https://api.dida365.com`.
5. **OAuth credentials stay local:** open-source project must not ship private client secrets. Users configure their own developer app credentials.
6. **Safety:** ambiguous fuzzy matches must refuse to mutate data unless an exact ID or explicit disambiguation is used.
7. **TDD:** production behavior should be covered by tests; write tests first for core logic and CLI behavior.

## Target Commands for MVP

### Auth / config

- `ticktask auth init --service {ticktick,dida365} --client-id ... --client-secret ... --redirect-uri ...`
- `ticktask auth status [--json]`
- `ticktask doctor [--json]`
- `ticktask config path`

### Project

- `ticktask project list [--json]`
- `ticktask project get <project>`
- `ticktask project data <project>`

### Task

- `ticktask task list [--project NAME_OR_ID] [--status open|completed|all] [--json]`
- `ticktask task search <query> [--json]`
- `ticktask task add TITLE [--project NAME] [--content TEXT] [--due DATE] [--priority none|low|medium|high] [--json]`
- `ticktask task complete TASK_ID [--project-id PROJECT_ID] [--yes] [--json]`
- aliases: `ticktask today`, `ticktask add`, `ticktask done`

### MCP MVP tools

- `ticktask_doctor`
- `ticktask_auth_status`
- `ticktask_list_projects`
- `ticktask_list_tasks`
- `ticktask_search_tasks`
- `ticktask_create_task`
- `ticktask_complete_task`
- `ticktask_today`

## Stable JSON Shape

Success:

```json
{"ok": true, "data": {}, "meta": {}}
```

Error:

```json
{"ok": false, "error": {"code": "ERROR_CODE", "message": "Human message", "hint": "Optional next step"}}
```

## Implementation Tasks

### Task 1: Bootstrap package skeleton

**Objective:** Create installable Python package with CLI entry points and test tooling.

**Files:**
- Create: `pyproject.toml`
- Create: `README.md`
- Create: `LICENSE`
- Create: `src/ticktask/__init__.py`
- Create: `src/ticktask/cli/app.py`
- Create: `tests/test_cli_smoke.py`

**Acceptance:**
- `uv run ticktask --help` works.
- `uv run tt --help` works.
- `uv run pytest -q` passes.

### Task 2: Core error/result model

**Objective:** Define reusable structured result and exception types.

**Files:**
- Create: `src/ticktask/core/errors.py`
- Create: `src/ticktask/core/results.py`
- Test: `tests/core/test_results.py`

**Acceptance:**
- Exceptions convert to JSON error shape.
- CLI can emit JSON success/error consistently.

### Task 3: Service profiles and config

**Objective:** Implement config paths and service profile selection for TickTick/Dida365.

**Files:**
- Create: `src/ticktask/core/constants.py`
- Create: `src/ticktask/core/config.py`
- Test: `tests/core/test_config.py`

**Acceptance:**
- `dida365` resolves to `https://api.dida365.com`.
- `ticktick` resolves to `https://api.ticktick.com`.
- Config writes to XDG-style path, overridable with `TICKTASK_CONFIG_DIR` for tests.
- No user secrets in repo.

### Task 4: OAuth/token storage interface

**Objective:** Add local config credential storage and auth status without requiring real network login yet.

**Files:**
- Create: `src/ticktask/core/auth.py`
- Create/Modify: `src/ticktask/cli/auth.py`
- Test: `tests/core/test_auth.py`, `tests/cli/test_auth_cli.py`

**Acceptance:**
- `ticktask auth init ...` stores service/client config.
- `ticktask auth status --json` reports configured/login/token status.
- Missing config returns actionable error.

### Task 5: HTTP client and project/task services

**Objective:** Implement API client methods over official Open API endpoints with testable injected transport.

**Files:**
- Create: `src/ticktask/core/client.py`
- Create: `src/ticktask/core/services.py`
- Create: `src/ticktask/core/models.py`
- Test: `tests/core/test_client.py`, `tests/core/test_services.py`

**Acceptance:**
- Client adds Bearer token.
- Supports `/open/v1/project`, `/open/v1/project/{id}/data`, `/open/v1/task`, complete endpoint.
- Dida365 completed endpoint must support calls without `projectIds` to avoid known missing-data pitfall.

### Task 6: CLI project/task commands

**Objective:** Implement human-readable and JSON command surface for project/task MVP.

**Files:**
- Create: `src/ticktask/cli/project.py`
- Create: `src/ticktask/cli/task.py`
- Create: `src/ticktask/cli/formatters.py`
- Modify: `src/ticktask/cli/app.py`
- Test: `tests/cli/test_project_cli.py`, `tests/cli/test_task_cli.py`

**Acceptance:**
- Commands parse correctly.
- `--json` output is stable.
- Ambiguous task completion by search term refuses mutation; ID completion is allowed with `--yes`.

### Task 7: MCP server MVP

**Objective:** Expose MCP tools using the same core services.

**Files:**
- Create: `src/ticktask/mcp/server.py`
- Create: `src/ticktask/mcp/tools.py`
- Create: `src/ticktask/mcp/schemas.py`
- Test: `tests/mcp/test_tools.py`

**Acceptance:**
- `ticktask-mcp` entry point starts stdio MCP server when `mcp` package is installed.
- Tool functions can be unit-tested without launching stdio transport.
- MCP tool outputs use the same result/error model.
- If MCP package is missing, CLI gives a clear install hint.

### Task 8: Docs and agent usage

**Objective:** Document installation, OAuth setup, CLI usage, MCP config, and safety model.

**Files:**
- Modify: `README.md`
- Create: `docs/installation.md`
- Create: `docs/oauth.md`
- Create: `docs/cli-usage.md`
- Create: `docs/mcp-usage.md`
- Create: `docs/agent-usage.md`

**Acceptance:**
- README shows human CLI, agent JSON, Dida365, and MCP examples.
- No private credentials or local-only assumptions.

## Codex Execution Instructions

Codex should implement the MVP in one coherent pass, but preserve the architecture above. It should prefer tested core logic over superficial UI polish. It must not include real credentials. It may use mocked HTTP responses for tests.

Run before finishing:

```bash
uv run pytest -q
uv run ticktask --help
uv run ticktask doctor --json
uv run ticktask auth status --json
```

If dependency resolution fails, update `pyproject.toml` appropriately and document the reason.

## Review Checklist for Hermes

- [ ] Repository exists under `/Users/geekmai/Documents/Code/ticktask`.
- [ ] Shared core exists; CLI and MCP do not duplicate API logic.
- [ ] Dida365 service profile is correct.
- [ ] No credentials committed.
- [ ] Tests pass.
- [ ] CLI entry points work.
- [ ] MCP module has testable tool functions and install hint.
- [ ] JSON output/error model is stable.
- [ ] README explains CLI + MCP + Agent usage.
