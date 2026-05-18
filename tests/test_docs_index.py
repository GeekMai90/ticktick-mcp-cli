from pathlib import Path
import re


DOCS_INDEX = Path("docs/index.md")
README = Path("README.md")
README_ZH = Path("README.zh-CN.md")
ROADMAP = Path("docs/roadmap.md")
PYPROJECT = Path("pyproject.toml")

REQUIRED_DOC_LINKS = [
    "agent-quickstart.md",
    "installation.md",
    "oauth.md",
    "cli-usage.md",
    "mcp-usage.md",
    "integrations.md",
    "agent-usage.md",
    "release.md",
    "roadmap.md",
]


def _markdown_links(text: str) -> list[str]:
    return re.findall(r"\[[^\]]+\]\(([^)]+)\)", text)


def test_docs_index_exists_as_agent_and_human_landing_page() -> None:
    index = DOCS_INDEX.read_text()

    assert "# TickTick MCP CLI Docs" in index
    assert "Start here" in index
    assert "agent-first" in index.lower()
    assert "Dida365" in index
    assert "doctor --json" in index
    assert "auth status --json" in index
    assert "Do not create, update, complete, or delete tasks" in index


def test_docs_index_links_all_primary_docs_with_relative_paths() -> None:
    index = DOCS_INDEX.read_text()

    for link in REQUIRED_DOC_LINKS:
        assert f"]({link})" in index
        assert (DOCS_INDEX.parent / link).exists()

    assert "docs/agent-quickstart.md" not in index


def test_public_readmes_link_docs_index_from_repository_root() -> None:
    assert "docs/index.md" in README.read_text()
    assert "docs/index.md" in README_ZH.read_text()


def test_docs_index_markdown_links_resolve() -> None:
    missing = []
    for target in _markdown_links(DOCS_INDEX.read_text()):
        if target.startswith(("http://", "https://", "#", "mailto:")):
            continue
        path = target.split("#", 1)[0]
        if path and not (DOCS_INDEX.parent / path).exists():
            missing.append(target)

    assert missing == []


def test_roadmap_marks_lightweight_docs_index_complete() -> None:
    roadmap = ROADMAP.read_text()
    pyproject = PYPROJECT.read_text()

    assert '"docs"' in pyproject
    assert "[x] Lightweight docs index for agent-first onboarding" in roadmap
    assert "✅ `feat(docs): add lightweight docs index`" in roadmap
