# Phase 3: OAuth hardening, automatic refresh, and CI

## Goal

Move ticktask from a local MVP toward a safer installable tool by hardening OAuth, refreshing tokens automatically, and adding repository CI.

## Scope

1. OAuth hardening
   - Generate state values for authorization URLs.
   - Support PKCE code verifier/challenge generation.
   - Preserve the current copy-code login path for non-browser and testable flows.
   - Add tests proving state and PKCE parameters are present and code exchange sends the verifier.

2. Automatic token refresh
   - Detect expired or near-expired access tokens before API calls.
   - Refresh automatically when a refresh token is available.
   - Keep unauthenticated/missing-token errors clear when refresh is impossible.
   - Add tests for expired, near-expired, valid, and malformed expiry values.

3. Local callback helper
   - Keep it minimal and safe: parse a callback URL/query for `code` and `state` validation.
   - Defer a long-running local HTTP callback server unless needed after this phase.

4. CI
   - Add GitHub Actions running formatting/import checks if available plus tests on supported Python versions.
   - Keep CI dependency installation compatible with uv.

## Out of scope for this phase

- Habit/focus endpoints until the official Open API surface is verified.
- PyPI release automation.
- Publishing a GitHub repository or pushing remotes without explicit approval.

## Verification

Run:

```bash
uv run pytest -q
uv run ticktask --help
uv run ticktask doctor --json
uv run ticktask auth status --json
uv run --with 'mcp>=1.0' python -c 'from ticktask.mcp.server import build_server; build_server(); print("mcp_build_ok")'
```

Also check:

```bash
git status --short
git diff --check
```
