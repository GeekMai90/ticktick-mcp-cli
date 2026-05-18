# TickTick MCP CLI Docs

Start here if you are a human user or an AI agent installing TickTick MCP CLI from a repository link. This docs index is intentionally lightweight so it works well on GitHub Pages, GitHub's Markdown renderer, and agent context windows.

## Start here

- [Agent-First Quickstart](agent-quickstart.md) — fastest path when a user gives an agent this repository link and asks it to install/configure the tool.
- [Installation](installation.md) — install script, GitHub npx wrapper, PyPI/uv/pipx, source build, and config directory notes.
- [OAuth](oauth.md) — OAuth app setup, PKCE/state login flow, keyring token storage, and local callback server mode.

Recommended agent health checks after installation:

```bash
ticktick-mcp-cli doctor --json
ticktick-mcp-cli auth status --json
```

Read-only smoke prompt for MCP clients:

```text
List my projects. Do not create, update, complete, or delete tasks.
```

## Agent-facing operation guides

- [Agent Usage](agent-usage.md) — JSON-first command rules, safe mutations, destructive confirmations, and secret-handling rules.
- [MCP Usage](mcp-usage.md) — MCP tools/resources/prompts exposed over the shared core.
- [MCP Runtime Integrations](integrations.md) — Claude Desktop, Hermes, Cursor, Claude Code, and OpenClaw configuration examples.

## Human-facing command references

- [CLI Usage](cli-usage.md) — command groups and examples for tasks, projects, habits, focus, sync, backup, analytics, diagnostics, and auth.
- [Release Checklist](release.md) — PyPI/TestPyPI trusted publishing and release verification.
- [Roadmap](roadmap.md) — completed features and remaining roadmap.

## Service notes

- Dida365 is first-class. Prefer `--service dida365` when the user is in the Chinese/domestic TickTick context.
- Global completed-task queries intentionally omit `projectIds` unless the user explicitly scopes to a project.
- Do not print or store raw `client_secret`, `access_token`, or `refresh_token` values in agent summaries.

## Copy/paste install paths

Installer script:

```bash
curl -fsSL https://raw.githubusercontent.com/GeekMai90/ticktick-mcp-cli/main/scripts/install.sh | sh
```

GitHub npx wrapper:

```bash
npx github:GeekMai90/ticktick-mcp-cli doctor --json
npx github:GeekMai90/ticktick-mcp-cli auth status --json
npx --package github:GeekMai90/ticktick-mcp-cli ticktick-mcp
```
