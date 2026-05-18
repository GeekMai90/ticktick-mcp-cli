# Agent-First Quickstart

You are an AI agent helping a user connect TickTick or Dida365 to a CLI/MCP runtime. Follow this path when the user gives you this repository link and asks you to install or configure it.

## 0. Operating rules for agents

- Prefer JSON output and branch on `ok`, `error.code`, and explicit fields.
- Never print `client_secret`, `access_token`, or `refresh_token` values. Treat `*_configured` booleans as enough evidence that a secret exists.
- Do not create, update, complete, move, or delete tasks during setup unless the user explicitly asks for a write operation.
- If a command fails, read the JSON error or stderr hint, fix the prerequisite, and retry once. If it still fails, report the exact command and redacted error.

## 1. Install

Use the install script when you can run shell commands on the user's machine:

```bash
curl -fsSL https://raw.githubusercontent.com/GeekMai90/ticktick-mcp-cli/main/scripts/install.sh | sh
```

If the runtime already has Node.js and the user prefers an ephemeral launch, use the GitHub npx wrapper:

```bash
npx github:GeekMai90/ticktick-mcp-cli doctor --json
npx github:GeekMai90/ticktick-mcp-cli auth status --json
```

For isolated agent work, set `TICKTASK_CONFIG_DIR` before auth so you do not mix credentials between runtimes:

```bash
export TICKTASK_CONFIG_DIR="$HOME/.config/ticktask-agent"
```

## 2. Health check

After installation, run:

```bash
ticktick-mcp-cli doctor --json
ticktick-mcp-cli auth status --json
```

Interpretation:

- `doctor --json` checks local runtime health and safe diagnostics.
- `auth status --json` tells you whether OAuth credentials and tokens are configured without printing secret values.
- If `token_storage` is `keyring`, use `keyring_available` and `keyring_hint` to decide whether the OS keyring is usable.

## 3. Initialize OAuth app credentials

Dida365 is first-class. Prefer Dida365 when the user is in the Chinese/domestic service context:

```bash
ticktick-mcp-cli auth init \
  --service dida365 \
  --client-id "$DIDA365_CLIENT_ID" \
  --client-secret "$DIDA365_CLIENT_SECRET" \
  --redirect-uri "http://localhost:8080/callback" \
  --token-storage keyring \
  --json
```

For international TickTick, switch only the service and environment variables:

```bash
ticktick-mcp-cli auth init \
  --service ticktick \
  --client-id "$TICKTICK_CLIENT_ID" \
  --client-secret "$TICKTICK_CLIENT_SECRET" \
  --redirect-uri "http://localhost:8080/callback" \
  --token-storage keyring \
  --json
```

Never print the `client_secret`. If keyring is unavailable, the command returns a clear status/hint instead of silently downgrading storage.

## 4. Complete OAuth login

Use the local one-shot callback server when the redirect URI is localhost with an explicit port:

```bash
ticktick-mcp-cli auth login --service dida365 --local-server --json
```

The command opens the browser, receives one callback on `http://localhost:8080/callback`, validates state and PKCE, exchanges the code, stores tokens, and exits. Do not print OAuth codes, `access_token`, or `refresh_token` values.

If browser automation or localhost callback is unavailable, use the manual fallback from `auth login --json` and ask the user to paste only the callback URL/code through the CLI prompt path.

## 5. Configure MCP runtime

Use the stdio MCP server command:

```json
{
  "mcpServers": {
    "ticktick": {
      "command": "ticktick-mcp",
      "args": []
    }
  }
}
```

If PATH is unreliable in the target runtime, resolve the absolute binary path first:

```bash
command -v ticktick-mcp
```

For ephemeral Node-based runtimes, use:

```bash
npx --package github:GeekMai90/ticktick-mcp-cli ticktick-mcp
```

## 6. Read-only smoke test

Ask the MCP client or CLI to do a read-only smoke test:

```text
List my projects. Do not create, update, complete, or delete tasks.
```

CLI equivalent:

```bash
ticktick-mcp-cli project list --json
```

For real API integration smoke, only run the gated read-only check when the user explicitly allows it:

```bash
TICKTASK_INTEGRATION=1 ticktick-mcp-cli integration smoke --service dida365 --json
```

## 7. Safe handoff summary

When setup finishes, report only:

- install path used: install script, PyPI/uv/pipx, or GitHub npx wrapper;
- service: `dida365` or `ticktick`;
- `auth status --json` fields that are not secrets;
- MCP command configured;
- read-only smoke-test result.

Never include raw OAuth tokens or local secret file contents in the summary.
