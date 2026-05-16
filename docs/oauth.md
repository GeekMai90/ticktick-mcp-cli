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

The MVP stores OAuth app config and token fields in the local config file. Full interactive browser login is intentionally minimal in this version; the structure is present so a browser flow can be added without changing CLI or MCP consumers.

Never commit local config, client secrets, access tokens, or refresh tokens.
