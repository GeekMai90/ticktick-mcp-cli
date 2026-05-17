from pathlib import Path


INTEGRATIONS_INDEX = Path("docs/integrations.md")
INTEGRATION_DOCS = {
    "Claude Desktop": Path("docs/integrations/claude-desktop.md"),
    "Hermes": Path("docs/integrations/hermes.md"),
    "Cursor": Path("docs/integrations/cursor.md"),
    "Claude Code": Path("docs/integrations/claude-code.md"),
    "OpenClaw": Path("docs/integrations/openclaw.md"),
}
README = Path("README.md")
README_ZH = Path("README.zh-CN.md")
ROADMAP = Path("docs/roadmap.md")


def test_integration_index_links_all_supported_agent_runtimes() -> None:
    index = INTEGRATIONS_INDEX.read_text()

    for name, path in INTEGRATION_DOCS.items():
        assert name in index
        assert str(path).replace("docs/", "") in index

    assert "ticktick-mcp" in index
    assert "uv tool install 'ticktick-mcp-cli[mcp]'" in index


def test_each_runtime_doc_has_copy_pasteable_mcp_server_config() -> None:
    for name, path in INTEGRATION_DOCS.items():
        text = path.read_text()
        assert name in text
        assert "ticktick-mcp" in text
        assert "ticktick-mcp-cli[mcp]" in text
        assert "ticktick-mcp-cli doctor --json" in text
        assert "ticktick-mcp-cli auth status --json" in text
        assert "TICKTASK_CONFIG_DIR" in text
        assert "dida365" in text


def test_json_based_runtime_docs_include_mcpservers_snippet() -> None:
    for name in ["Claude Desktop", "Cursor"]:
        text = INTEGRATION_DOCS[name].read_text()
        assert '"mcpServers"' in text
        assert '"ticktick"' in text
        assert '"command": "ticktick-mcp"' in text


def test_readmes_and_roadmap_reference_integration_examples() -> None:
    readme = README.read_text()
    readme_zh = README_ZH.read_text()
    roadmap = ROADMAP.read_text()

    assert "docs/integrations.md" in readme
    assert "Claude Desktop" in readme
    assert "Hermes" in readme
    assert "docs/integrations.md" in readme_zh
    assert "Claude Desktop" in readme_zh
    assert "Hermes" in readme_zh
    assert "[x] Example configs for Claude Desktop, Hermes, Cursor, Claude Code, and OpenClaw" in roadmap
    assert "✅ `feat(config): add MCP integration examples for agent runtimes`" in roadmap
