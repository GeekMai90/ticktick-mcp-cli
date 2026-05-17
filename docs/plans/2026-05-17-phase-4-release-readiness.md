# Phase 4: Release readiness and integration smoke

## Goal

Prepare ticktask for a first public/package release without creating or pushing a remote repository yet.

## Scope

1. Release metadata
   - Add standard project metadata for PyPI/GitHub discovery.
   - Add license and package manifest hygiene.
   - Keep package contents source-only and avoid generated caches.

2. Build verification
   - Ensure `uv build` produces a source distribution and wheel.
   - Add CI build check so packaging regressions are caught.

3. Explicit integration smoke path
   - Add a CLI command that runs read-only real API checks only when explicitly enabled.
   - Require `TICKTASK_INTEGRATION=1` to avoid accidental network/API use.
   - Keep it read-only: auth status + project list count.
   - Support stable JSON output for agents.

4. Documentation
   - Document release preparation steps.
   - Document integration smoke prerequisites and safety behavior.

## Out of scope

- Creating a GitHub remote repository or pushing code; this is an external side effect and should be done only after explicit confirmation.
- Publishing to PyPI/TestPyPI.
- Habit/focus endpoints until official Open API coverage is confirmed.

## Verification

```bash
uv run pytest -q
uv run ticktask integration smoke --json
TICKTASK_INTEGRATION=1 uv run ticktask integration smoke --json
uv build
uv run --with 'mcp>=1.0' python -c 'from ticktask.mcp.server import build_server; build_server(); print("mcp_build_ok")'
git diff --check
```
