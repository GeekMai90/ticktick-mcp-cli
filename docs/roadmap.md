# TickTick MCP CLI Roadmap

This roadmap converts competitor strengths into an implementation backlog. The project goal is not merely parity with existing TickTick/Dida365 MCP tools; it is to become the safest, most complete, and most agent-friendly task automation layer for both humans and AI agents.

## Product principles

- **Official API first**: prefer TickTick/Dida365 Open API and OAuth over username/password, cookie auth, or private endpoints.
- **CLI and MCP parity**: every durable capability should have both a human-friendly CLI command and an agent-friendly MCP tool backed by the same core service.
- **Stable automation contract**: JSON output must remain predictable: `ok`, `data`, `meta`, `error`.
- **Safe by default**: destructive writes require exact IDs and explicit confirmation flags.
- **Dida365 is first-class**: domestic Dida365 profiles must be tested and documented alongside international TickTick.
- **Agent handoff friendly**: README, command names, schemas, and errors should be clear enough for a fresh AI agent to operate safely.

## Competitive parity targets

### 1. Full task lifecycle

Source projects: `jacepark12/ticktick-mcp`, `alexarevalo9/ticktick-mcp-server`, `jen6/ticktick-mcp`.

- [x] List projects
- [x] Get project data
- [x] List/search/create/get/update/complete/delete/move tasks
- [x] Completed-task listing
- [x] Subtasks/checklist item CRUD
- [x] Tag-aware filters and tag operations
- [ ] Reminder create/update/delete
- [ ] Repeat/RRULE helpers
- [ ] Due/start date convenience parser and validator
- [ ] Priority/status/kind validation helpers
- [ ] Bulk complete/delete/move guarded by dry-run + confirmation

### 2. Project, folder, and kanban management

Source projects: `jacepark12/ticktick-mcp`, `ticktick-sdk`, `dida365-ai-tools`.

- [x] Project list and project data
- [x] Project create/update/delete
- [ ] Kanban columns list/create/update/delete when available through official APIs
- [ ] Folder/group awareness and filtering
- [ ] Archived/closed project handling
- [ ] Project templates for common workflows

### 3. Tags, filters, and saved views

Source projects: `jen6/ticktick-mcp`, `dida365-ai-tools`, `ticktick-sdk`.

- [ ] Tag-aware task list/search/filter
- [ ] Tag add/remove operations
- [ ] Smart filters: today, overdue, upcoming, high-priority, no-date, completed range
- [ ] Saved query presets for common agent workflows
- [ ] Natural-language query adapter that compiles to deterministic filters

### 4. Habits and focus sessions

Source project: `ticktick-sdk`; official Open API exposes habit/focus endpoints.

- [ ] Habit list/get/create/update
- [ ] Habit check-in create/update and history query
- [ ] Focus session list/get/delete
- [ ] Focus reporting exports
- [ ] MCP tools for habit/focus workflows

### 5. Batch, sync, and analytics

Source projects: `dida365-ai-tools`, `GalaxyXieyu/didatodolist-mcp`, `ticktick-sdk`.

- [ ] Batch task operations with dry-run preview
- [ ] Incremental sync/export state file
- [ ] Markdown/CSV/JSONL backups by project/date
- [ ] Task analytics: completed count, overdue count, project throughput, tag distribution
- [ ] Goal/progress reporting derived from tasks, habits, and focus sessions
- [ ] Conflict-safe retries and rate-limit handling

### 6. MCP excellence

Source projects: all MCP-first competitors.

- [x] MCP server over shared core
- [x] Core task tools
- [ ] One MCP tool for every CLI capability
- [ ] Rich JSON schemas with examples and enum constraints
- [ ] MCP resource endpoints for projects, config, and saved views
- [ ] Prompt templates for common workflows: daily planning, weekly review, cleanup, export
- [ ] Golden tests for MCP tool outputs

### 7. Distribution and developer experience

Source projects: `kvanland/ticktick-cli`, npm-based MCP servers.

- [x] GitHub install via `uv tool` / `pipx`
- [x] Public package name: `ticktick-mcp-cli`
- [x] Backward-compatible legacy commands: `ticktask`, `tt`, `ticktask-mcp`
- [ ] PyPI publishing workflow
- [ ] Homebrew tap or install script
- [ ] Optional npm wrapper for `npx ticktick-mcp-cli`
- [ ] Prebuilt docs site or GitHub Pages
- [ ] Example configs for Claude Desktop, Hermes, Cursor, Claude Code, and OpenClaw

### 8. Security and reliability

Project differentiator.

- [x] OAuth state and PKCE
- [x] Automatic token refresh
- [x] Destructive operations require exact IDs and `--yes`
- [x] Read-only smoke gate with `TICKTASK_INTEGRATION=1`
- [ ] Token storage keyring option
- [ ] Redacted diagnostic bundle command
- [ ] End-to-end OAuth callback local server mode
- [ ] Idempotency/deduplication helpers for agent retries
- [ ] Structured error taxonomy with remediation hints

## Suggested development phases

### Phase 1 — Rename and distribution polish

- Rename repository/package to `ticktick-mcp-cli`.
- Add public console aliases `ticktick-mcp-cli` and `ticktick-mcp` while keeping legacy commands.
- Update README, installation docs, and package metadata.
- Verify test suite, build artifacts, and GitHub remote.

### Phase 2 — Parity foundation

- Add project create/update/delete.
- Add subtasks/checklist CRUD.
- Add tag-aware filters and tag operations. ✅
- Ensure MCP parity for all new CLI commands.

### Phase 3 — Power-user features

- Add habits and focus sessions.
- Add reminders/repeat helpers.
- Add batch operations with dry-run and exact confirmation.
- Add analytics and report exports.

### Phase 4 — Best-in-class agent platform

- Add saved views, prompt templates, and MCP resources.
- Add optional npm wrapper and PyPI release automation.
- Add docs site with AI-agent quickstart recipes.
- Add OpenClaw/Hermes integration examples and golden traces.

## Near-term issue candidates

1. `feat(project): add create/update/delete project commands and MCP tools`
2. `feat(task): add checklist item CRUD for subtasks`
3. ✅ `feat(task): add tag filters and tag mutation helpers`
4. `feat(mcp): expose one tool per CLI capability with schema examples`
5. `feat(habit): add official habit list/checkin support`
6. `feat(focus): add official focus session query/export support`
7. `feat(batch): add dry-run guarded bulk operations`
8. `feat(dx): add PyPI publish workflow and install docs`
