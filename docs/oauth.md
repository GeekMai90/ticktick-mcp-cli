# OAuth

`ticktask` does not ship OAuth client secrets. Create your own TickTick or Dida365 developer app and store the credentials locally.

```bash
uv run ticktick-mcp-cli auth init \
  --service ticktick \
  --client-id "$TICKTICK_CLIENT_ID" \
  --client-secret "$TICKTICK_CLIENT_SECRET" \
  --redirect-uri "http://localhost:8080/callback"

# Optional: store client secret and tokens in the OS keyring instead of config.json.
# Install the optional extra first: pipx install 'ticktick-mcp-cli[keyring]' or uv tool install 'ticktick-mcp-cli[keyring]'.
uv run ticktick-mcp-cli auth init \
  --service dida365 \
  --client-id "$DIDA365_CLIENT_ID" \
  --client-secret "$DIDA365_CLIENT_SECRET" \
  --redirect-uri "http://localhost:8080/callback" \
  --token-storage keyring
```

Supported services:

- `ticktick`: `https://api.ticktick.com`
- `dida365`: `https://api.dida365.com`

Check status:

```bash
uv run ticktick-mcp-cli auth status --json
```

Login flow:

```bash
uv run ticktick-mcp-cli auth login --service ticktick --local-server --json
uv run ticktick-mcp-cli auth login --service ticktick --no-browser --json
uv run ticktick-mcp-cli auth login --service ticktick --callback-url 'http://localhost:8080/callback?code=***&state=STATE' --json
uv run ticktick-mcp-cli auth login --service ticktick --code CALLBACK_CODE --state STATE --json
uv run ticktick-mcp-cli auth refresh --service ticktick --json
```

`auth login --local-server` starts a one-shot localhost callback server on the host, port, and path from your configured redirect URI (for example `http://localhost:8080/callback`), opens the authorization URL, validates OAuth state, exchanges the code, then exits. Use `--timeout SECONDS` to control how long it waits.

`auth login --no-browser` starts a hardened manual browser flow:

- generates and stores an OAuth `state` value;
- generates a PKCE code verifier and sends a `S256` code challenge;
- prints the authorization URL and state in JSON mode.

After the provider redirects to your configured callback URL, prefer passing the full callback URL with `--callback-url`; ticktask extracts the `code` and validates `state`. You can alternatively pass `--code` plus the printed `--state`. The code exchange sends the stored PKCE verifier, clears one-time OAuth state/verifier after success, uses `/oauth/token`, updates the local access token, preserves refresh tokens when the provider omits a new one, and tracks `expires_at` from `expires_in`.

Before API calls, ticktask automatically refreshes expired or near-expired access tokens when a refresh token is available. If the access token is expired and no refresh token exists, commands fail with an explicit login hint.

The local callback server intentionally accepts only explicit-port `http://localhost` or `http://127.0.0.1` redirect URIs and handles one callback request before shutting down.

Never commit local config, client secrets, access tokens, or refresh tokens. `auth status --json`, `doctor --json`, diagnostic bundles, and the `ticktask://config` MCP resource expose only boolean `*_configured` flags plus `token_storage`/keyring availability; they never return secret values.
