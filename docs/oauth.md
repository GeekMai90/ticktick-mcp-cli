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
uv run ticktask auth login --service ticktick --code CALLBACK_CODE --json
uv run ticktask auth refresh --service ticktick --json
```

`auth login --no-browser` prints a deterministic authorization URL. After the provider redirects to your configured callback URL, copy the `code` query parameter and pass it with `--code`. The code exchange and refresh calls use `/oauth/token`, update the local access token, preserve refresh tokens when the provider omits a new one, and track `expires_at` from `expires_in`.

This phase intentionally does not run a full local browser callback server. The implemented flow is robust and testable with mocked HTTP, and keeps all credentials local.

Never commit local config, client secrets, access tokens, or refresh tokens.
