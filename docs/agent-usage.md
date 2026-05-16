# Agent Usage

Prefer JSON commands:

```bash
uv run ticktask doctor --json
uv run ticktask auth status --json
uv run ticktask project list --json
uv run ticktask task list --json
uv run ticktask task search "query" --json
```

Rules for agents:

- Treat `ok: false` as a failed operation.
- Branch on `error.code` instead of parsing human text.
- Do not mutate by fuzzy match.
- Complete tasks only with exact `TASK_ID`, exact `PROJECT_ID`, and `--yes`.
- Never print or commit local config, access tokens, refresh tokens, client secrets, or user-local paths unless the user explicitly asks for diagnostic output.

Mutation example:

```bash
uv run ticktask task complete TASK_ID --project-id PROJECT_ID --yes --json
```

The command refuses non-confirmed completion and returns a stable `CONFIRMATION_REQUIRED` error.
