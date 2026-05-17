# Release Checklist

This project is not published automatically yet. Use this checklist before creating a public GitHub repository, GitHub release, TestPyPI release, or PyPI release.

## Local verification

```bash
uv sync --all-extras --dev
uv run pytest -q
uv run ticktick-mcp-cli --help
uv run ticktick-mcp-cli doctor --json
uv run ticktick-mcp-cli integration smoke --json
uv run --with 'mcp>=1.0' python -c 'from ticktask.mcp.server import build_server; build_server(); print("mcp_build_ok")'
uv build
git diff --check
```

## Optional real API smoke

Only run this when a local service profile has real OAuth credentials/tokens and the account is safe to inspect:

```bash
TICKTASK_INTEGRATION=1 uv run ticktick-mcp-cli integration smoke --service dida365 --json
```

The smoke command is read-only and lists projects to confirm authentication and API reachability. It does not create, update, complete, move, or delete tasks.

## GitHub publication

Do this only after explicit approval from the repository owner:

```bash
gh repo create ticktask --public --source . --push \
  --description "Agent-friendly CLI and MCP server for TickTick and Dida365"
```

Recommended topics after creation:

```bash
gh repo edit --add-topic ticktick,dida365,cli,mcp,task-management,agents
```

## PyPI/TestPyPI

1. Confirm `pyproject.toml` version.
2. Build clean artifacts:

   ```bash
   rm -rf dist
   uv build
   ```

3. Inspect artifacts:

   ```bash
   python -m zipfile -l dist/*.whl
   tar -tzf dist/*.tar.gz | head
   ```

4. Publish to TestPyPI first, then PyPI after install testing succeeds.

Do not include local config, OAuth client secrets, access tokens, refresh tokens, or `.env` files in any artifact.
