# Release Checklist

Use this checklist before creating a GitHub release, TestPyPI release, or PyPI release. The repository has a GitHub Actions publishing workflow backed by PyPI Trusted Publishing, so maintainers should not store long-lived PyPI API tokens in repository secrets.

## Local verification

```bash
uv sync --all-extras --dev
uv run pytest -q
uv run ticktick-mcp-cli --help
uv run ticktick-mcp-cli doctor --json
uv run ticktick-mcp-cli integration smoke --json
uv run --with 'mcp>=1.0' python -c 'from ticktask.mcp.server import build_server; build_server(); print("mcp_build_ok")'
rm -rf dist
uv build
uvx twine check dist/*
git diff --check
```

## Optional real API smoke

Only run this when a local service profile has real OAuth credentials/tokens and the account is safe to inspect:

```bash
TICKTASK_INTEGRATION=1 uv run ticktick-mcp-cli integration smoke --service dida365 --json
```

The smoke command is read-only and lists projects to confirm authentication and API reachability. It does not create, update, complete, move, or delete tasks.

## Trusted Publishing setup

Configure PyPI and TestPyPI Trusted Publishing once per project:

- PyPI project: `ticktick-mcp-cli`
- Owner/repository: `GeekMai90/ticktick-mcp-cli`
- Workflow filename: `publish.yml`
- PyPI environment: `pypi`
- TestPyPI environment: `testpypi`

Recommended GitHub environments:

- `testpypi`: no required reviewers, used for manual release rehearsal.
- `pypi`: require maintainer approval before the publish job can mint an OIDC token.

The workflow grants `id-token: write` only to the publish jobs and uses `pypa/gh-action-pypi-publish@release/v1`, so no `PYPI_API_TOKEN` secret is required.

## GitHub publication

Do this only after explicit approval from the repository owner:

```bash
gh repo create ticktick-mcp-cli --public --source . --push \
  --description "Agent-friendly CLI and MCP server for TickTick and Dida365"
```

Recommended topics after creation:

```bash
gh repo edit --add-topic ticktick,dida365,cli,mcp,task-management,agents
```

## TestPyPI rehearsal

1. Confirm `pyproject.toml` version and changelog/release notes.
2. Run the local verification checklist above.
3. Trigger the manual workflow:

   ```bash
   gh workflow run publish.yml -f target=testpypi
   gh run watch --exit-status
   ```

4. Install from TestPyPI in a clean environment:

   ```bash
   python -m venv /tmp/ticktask-testpypi
   /tmp/ticktask-testpypi/bin/python -m pip install \
     --index-url https://test.pypi.org/simple/ \
     --extra-index-url https://pypi.org/simple/ \
     'ticktick-mcp-cli[mcp]'
   /tmp/ticktask-testpypi/bin/ticktick-mcp-cli --version
   /tmp/ticktask-testpypi/bin/ticktick-mcp-cli doctor --json
   ```

## PyPI release

Publish to PyPI from a GitHub release. Use a version tag matching `pyproject.toml`:

```bash
gh release create v0.1.0 \
  --title "v0.1.0" \
  --notes-file /tmp/ticktick-mcp-cli-release-notes.md
```

The `Publish Python Package` workflow runs on `release.published` and publishes to the `pypi` environment. Maintainers can also trigger `workflow_dispatch` with `target=pypi` for an approved manual retry.

After publish, verify the public package:

```bash
uv tool install ticktick-mcp-cli
uv tool run ticktick-mcp-cli --version
pipx install ticktick-mcp-cli
```

Do not include local config, OAuth client secrets, access tokens, refresh tokens, `.env` files, or generated `dist/` artifacts in source control or release archives.
