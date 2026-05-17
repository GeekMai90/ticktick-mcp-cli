# TickTick MCP CLI

[简体中文](README.zh-CN.md) | English

Agent-friendly CLI and MCP server for TickTick international and Dida365 domestic APIs.

TickTick MCP CLI is designed for both human operators and AI agents:

- **Humans** get readable terminal commands for projects, tasks, completed tasks, exports, OAuth, and diagnostics.
- **AI agents** get stable JSON output, explicit safety checks, deterministic command shapes, and an MCP server exposing the same core capabilities.

If you paste this repository link into an agent, the agent should be able to install the project, check authentication, list projects/tasks, and use the MCP tools by following this README alone.

## What it does

TickTick MCP CLI provides a shared Python core with two thin frontends:

- **CLI**: `ticktick-mcp-cli`, legacy `ticktask`, and short alias `tt`.
- **MCP server**: `ticktick-mcp` and legacy `ticktask-mcp` for agent runtimes that support Model Context Protocol.

Supported service profiles:

- `ticktick` → `https://api.ticktick.com`
- `dida365` → `https://api.dida365.com`

Current capabilities:

- OAuth credential setup and login.
- OAuth state + PKCE hardened authorization flow.
- Automatic access-token refresh when `expires_at` is near or past expiry.
- Project list and project data retrieval.
- Task list/search/create/get/update/complete/delete/move.
- Completed-task listing through the official `POST /open/v1/task/completed` API.
- Export tasks/completed tasks as `json`, `jsonl`, `csv`, or `markdown`.
- Read-only real API smoke check gated by `TICKTASK_INTEGRATION=1`.
- MCP tools over the same core behavior.

## Install

### Option A: use directly from a clone

```bash
git clone https://github.com/GeekMai90/ticktick-mcp-cli.git
cd ticktick-mcp-cli
uv sync --all-extras --dev
uv run ticktask --help
uv run tt --help
```

### Option B: install from GitHub

```bash
uv tool install git+https://github.com/GeekMai90/ticktick-mcp-cli.git
# or
pipx install git+https://github.com/GeekMai90/ticktick-mcp-cli.git
```

Then verify:

```bash
ticktick-mcp-cli --version
ticktick-mcp-cli doctor --json
```

Console scripts:

- `ticktick-mcp-cli` — main public CLI.
- `ticktask` — backward-compatible legacy CLI.
- `tt` — short CLI alias.
- `ticktick-mcp` — main public stdio MCP server.
- `ticktask-mcp` — backward-compatible legacy MCP server.

## Quick start for humans

### 1. Initialize OAuth app credentials

Create a TickTick or Dida365 developer OAuth app, then store its credentials locally:

```bash
ticktask auth init \
  --service ticktick \
  --client-id "$TICKTICK_CLIENT_ID" \
  --client-secret "$TICKTICK_CLIENT_SECRET" \
  --redirect-uri "http://localhost:8080/callback"
```

For Dida365, use:

```bash
ticktask auth init \
  --service dida365 \
  --client-id "$DIDA365_CLIENT_ID" \
  --client-secret "$DIDA365_CLIENT_SECRET" \
  --redirect-uri "http://localhost:8080/callback"
```

Local config path:

```bash
ticktask config path
```

Do **not** commit local config files, client secrets, access tokens, or refresh tokens.

### 2. Log in with OAuth

Start the browser/manual login flow:

```bash
ticktask auth login --service ticktick --no-browser --json
```

Open the returned `authorization_url`. After the provider redirects to your callback URL, complete login with either the full callback URL:

```bash
ticktask auth login \
  --service ticktick \
  --callback-url 'http://localhost:8080/callback?code=CALLBACK_CODE&state=STATE' \
  --json
```

or with code + state:

```bash
ticktask auth login --service ticktick --code CALLBACK_CODE --state STATE --json
```

Check status:

```bash
ticktask auth status --json
```

### 3. Use tasks

```bash
ticktask project list
ticktask task list
ticktask today
ticktask add "Plan release" --project Inbox
ticktask task search "release"
ticktask completed today
```

Mutating dangerous operations require exact IDs and explicit confirmation:

```bash
ticktask task complete TASK_ID --project-id PROJECT_ID --yes
ticktask task delete TASK_ID --project-id PROJECT_ID --yes
ticktask task move TASK_ID --from-project-id PROJECT_ID --to-project-id OTHER_PROJECT_ID
```

Export examples:

```bash
ticktask export tasks --format jsonl --status all
ticktask export tasks --format csv --project Inbox
ticktask export completed --format markdown --from 2026-05-01 --to 2026-05-17
```

## Quick start for AI agents

### Agent operating contract

When using `ticktask` from an agent:

1. Prefer `--json` for all CLI commands that support it.
2. Branch on `ok` first, then on `error.code` when `ok` is false.
3. Never infer task/project IDs from names before mutations; list/search first, then use exact IDs.
4. Pass `--yes` only after verifying the exact target of `complete` or `delete`.
5. Treat `TICKTASK_INTEGRATION=1` as permission to make read-only real API calls only.
6. Never print or commit OAuth client secrets, access tokens, refresh tokens, local config files, or `.env` files.

### Stable JSON envelope

Success:

```json
{"ok": true, "data": {}, "meta": {}}
```

Error:

```json
{"ok": false, "error": {"code": "ERROR_CODE", "message": "Human message", "hint": "Next step"}}
```

### Agent-safe command sequence

```bash
# Discover state
ticktask doctor --json
ticktask auth status --json
ticktask project list --json

# Read tasks
ticktask task list --json
ticktask task list --status completed --from 2026-05-01 --to 2026-05-17 --json
ticktask task search "release" --json

# Mutate only after exact IDs are known
ticktask task add "Plan release" --project Inbox --json
ticktask task update TASK_ID --project-id PROJECT_ID --title "New title" --json
ticktask task complete TASK_ID --project-id PROJECT_ID --yes --json
ticktask task delete TASK_ID --project-id PROJECT_ID --yes --json

# Safe real-API smoke: skipped unless explicitly enabled
ticktask integration smoke --json
TICKTASK_INTEGRATION=1 ticktask integration smoke --service dida365 --json
```

## MCP server

Install optional MCP dependencies when working from a clone:

```bash
uv sync --extra mcp
uv run ticktick-mcp
```

If installed as a tool, run:

```bash
ticktick-mcp
```

The MCP server uses stdio and exposes the same shared core behavior as the CLI.

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

## Real API integration smoke

The integration smoke command is safe by default:

```bash
ticktask integration smoke --json
```

It returns `skipped: true` unless explicitly enabled.

To run a read-only real API check:

```bash
TICKTASK_INTEGRATION=1 ticktask integration smoke --service dida365 --json
```

This only lists projects and returns `project_count`. It does not create, update, complete, move, or delete tasks.

## Development

```bash
git clone https://github.com/GeekMai90/ticktick-mcp-cli.git
cd ticktick-mcp-cli
uv sync --all-extras --dev
uv run pytest -q
uv run ticktick-mcp-cli --help
uv run ticktick-mcp-cli doctor --json
uv run --with 'mcp>=1.0' python -c 'from ticktask.mcp.server import build_server; build_server(); print("mcp_build_ok")'
```

Project notes:

- Keep CLI and MCP as thin frontends over `ticktask.core`.
- Preserve stable JSON envelopes for agent callers.
- Keep destructive actions explicit and ID-based.
- Do not commit OAuth secrets or local token files.

## Documentation

- [Installation](docs/installation.md)
- [OAuth](docs/oauth.md)
- [CLI Usage](docs/cli-usage.md)
- [MCP Usage](docs/mcp-usage.md)
- [Agent Usage](docs/agent-usage.md)
- [Release Checklist](docs/release.md)
- [Roadmap: competitive parity and best-in-class agent workflows](docs/roadmap.md)
- [Original Implementation Plan](docs/plans/2026-05-17-ticktask-cli-mcp-plan.md)

## Safety notes

- Local configuration is stored outside the repository by default.
- `.env`, token files, local config files, `dist/`, and build outputs are ignored by git.
- OAuth login uses state and PKCE.
- API calls auto-refresh expired or near-expired tokens when a refresh token is available.
- Completed-task listing intentionally omits `projectIds` for global queries to avoid missing Dida365 completed tasks.

## License

MIT. See [LICENSE](LICENSE).
