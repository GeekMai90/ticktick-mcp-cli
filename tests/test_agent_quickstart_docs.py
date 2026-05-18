from pathlib import Path


AGENT_QUICKSTART = Path("docs/agent-quickstart.md")
README = Path("README.md")
README_ZH = Path("README.zh-CN.md")
INSTALLATION_DOC = Path("docs/installation.md")
AGENT_USAGE_DOC = Path("docs/agent-usage.md")
ROADMAP = Path("docs/roadmap.md")
PYPROJECT = Path("pyproject.toml")


def test_agent_quickstart_exists_with_agent_first_install_and_healthcheck_flow() -> None:
    quickstart = AGENT_QUICKSTART.read_text()

    assert "# Agent-First Quickstart" in quickstart
    assert "You are an AI agent" in quickstart
    assert "curl -fsSL https://raw.githubusercontent.com/GeekMai90/ticktick-mcp-cli/main/scripts/install.sh | sh" in quickstart
    assert "npx github:GeekMai90/ticktick-mcp-cli doctor --json" in quickstart
    assert "ticktick-mcp-cli doctor --json" in quickstart
    assert "ticktick-mcp-cli auth status --json" in quickstart
    assert "TICKTASK_CONFIG_DIR" in quickstart


def test_agent_quickstart_covers_dida365_oauth_keyring_and_local_callback() -> None:
    quickstart = AGENT_QUICKSTART.read_text()

    assert "--service dida365" in quickstart
    assert "--token-storage keyring" in quickstart
    assert "--local-server" in quickstart
    assert "http://localhost:8080/callback" in quickstart
    assert "client_secret" in quickstart
    assert "access_token" in quickstart
    assert "refresh_token" in quickstart
    assert "Never print" in quickstart


def test_agent_quickstart_includes_mcp_runtime_and_read_only_smoke_prompt() -> None:
    quickstart = AGENT_QUICKSTART.read_text()

    assert "ticktick-mcp" in quickstart
    assert '"command": "ticktick-mcp"' in quickstart
    assert "read-only smoke test" in quickstart
    assert "List my projects" in quickstart
    assert "Do not create, update, complete, or delete tasks" in quickstart
    assert "If a command fails" in quickstart


def test_agent_quickstart_is_linked_from_public_docs() -> None:
    for path in (README, README_ZH):
        assert "docs/agent-quickstart.md" in path.read_text()
    for path in (INSTALLATION_DOC, AGENT_USAGE_DOC):
        assert "agent-quickstart.md" in path.read_text()
        assert "docs/agent-quickstart.md" not in path.read_text()


def test_agent_quickstart_is_packaged_and_roadmap_marks_complete() -> None:
    pyproject = PYPROJECT.read_text()
    roadmap = ROADMAP.read_text()

    assert '"docs"' in pyproject
    assert "[x] Agent-first quickstart for link-to-agent installs" in roadmap
    assert "✅ `feat(docs): add agent-first quickstart`" in roadmap
