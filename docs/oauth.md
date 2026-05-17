# OAuth

`ticktask` does not ship OAuth client secrets. Create your own TickTick or Dida365 developer app and store the credentials locally.

```bash
uv run ticktask auth init \
  --service ticktick \
  --client-id "$TICKTICK_CLIENT_ID" \
  --client-secret "$TICKTICK_CLIENT_SECRET" \
  --redirect-uri "http://localhost:8080/callback"
```

Supported services:

- `ticktick`: `https://api.ticktick.com`
- `dida365`: `https://api.dida365.com`

Check status:

```bash
uv run ticktask auth status --json
```

Login flow:

```bash
uv run ticktask auth login --service ticktick --no-browser --json
uv run ticktask auth login --service ticktick --callback-url 'http://localhost:8080/callback?code=CALLBACK_CODE&state=STATE' --json
uv run ticktask auth login --service ticktick --code CALLBACK_CODE --state STATE --json
uv run ticktask auth refresh --service ticktick --json
```

`auth login --no-browser` now starts a hardened browser flow:

- generates and stores an OAuth `state` value;
- generates a PKCE code verifier and sends a `S256` code challenge;
- prints the authorization URL and state in JSON mode.

After the provider redirects to your configured callback URL, prefer passing the full callback URL with `--callback-url`; ticktask extracts the `code` and validates `state`. You can alternatively pass `--code` plus the printed `--state`. The code exchange sends the stored PKCE verifier, clears one-time OAuth state/verifier after success, uses `/oauth/token`, updates the local access token, preserves refresh tokens when the provider omits a new one, and tracks `expires_at` from `expires_in`.

Before API calls, ticktask automatically refreshes expired or near-expired access tokens when a refresh token is available. If the access token is expired and no refresh token exists, commands fail with an explicit login hint.

This phase intentionally does not run a full local browser callback server. The implemented flow is robust and testable with mocked HTTP, and keeps all credentials local.

Never commit local config, client secrets, access tokens, or refresh tokens.
