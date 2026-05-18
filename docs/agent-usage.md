# Agent Usage

Prefer JSON commands:

```bash
uv run ticktick-mcp-cli doctor --json
uv run ticktick-mcp-cli auth status --json
uv run ticktick-mcp-cli project list --json
uv run ticktick-mcp-cli task list --json
uv run ticktick-mcp-cli task list --status completed --from 2026-05-01 --to 2026-05-17 --json
uv run ticktick-mcp-cli task search "query" --json
uv run ticktick-mcp-cli completed today --json
```

Rules for agents:

- Treat `ok: false` as a failed operation.
- Branch on `error.code` instead of parsing human text.
- Do not mutate by fuzzy match.
- Complete tasks only with exact `TASK_ID`, exact `PROJECT_ID`, and `--yes`.
- Delete tasks only with exact `TASK_ID`, exact `PROJECT_ID`, and `--yes`.
- Never print or commit local config, access tokens, refresh tokens, client secrets, or user-local paths unless the user explicitly asks for diagnostic output.
- Treat `token_storage: keyring` and `*_configured` booleans in `auth status`, diagnostics, and `ticktask://config` as secret-presence indicators only; never ask tools to reveal secret values.

Mutation example:

```bash
uv run ticktick-mcp-cli task complete TASK_ID --project-id PROJECT_ID --yes --json
uv run ticktick-mcp-cli task delete TASK_ID --project-id PROJECT_ID --yes --json
```

The commands refuse non-confirmed destructive operations and return a stable `CONFIRMATION_REQUIRED` error.

Exports are raw content, not result envelopes:

```bash
uv run ticktick-mcp-cli export tasks --format jsonl --status all --from 2026-05-01 --to 2026-05-17
uv run ticktick-mcp-cli export completed --format csv --from 2026-05-01 --to 2026-05-17
```
