from pathlib import Path


PAGES_WORKFLOW = Path(".github/workflows/docs-pages.yml")
DOCS_INDEX = Path("docs/index.md")
ROADMAP = Path("docs/roadmap.md")


def test_docs_pages_workflow_deploys_docs_with_github_pages_actions() -> None:
    workflow = PAGES_WORKFLOW.read_text()

    assert "name: Docs Pages" in workflow
    assert "workflow_dispatch:" in workflow
    assert "branches: [main]" in workflow
    assert "docs/**" in workflow
    assert "README.md" in workflow
    assert "pages: write" in workflow
    assert "id-token: write" in workflow
    assert "actions/configure-pages@v5" in workflow
    assert "enablement: true" in workflow
    assert "actions/jekyll-build-pages@v1" in workflow
    assert "actions/upload-pages-artifact@v3" in workflow
    assert "actions/deploy-pages@v4" in workflow
    assert "source: ./docs" in workflow
    assert "destination: ./_site" in workflow


def test_docs_pages_workflow_uses_single_deploy_environment_and_concurrency() -> None:
    workflow = PAGES_WORKFLOW.read_text()

    assert "environment:" in workflow
    assert "name: github-pages" in workflow
    assert "url: ${{ steps.deployment.outputs.page_url }}" in workflow
    assert "concurrency:" in workflow
    assert "group: pages" in workflow
    assert "cancel-in-progress: false" in workflow


def test_docs_index_is_pages_friendly_and_roadmap_marks_pages_workflow_complete() -> None:
    index = DOCS_INDEX.read_text()
    roadmap = ROADMAP.read_text()

    assert "# TickTick MCP CLI Docs" in index
    assert "GitHub Pages" in index
    assert "[x] GitHub Pages workflow for docs index" in roadmap
    assert "✅ `feat(docs): add GitHub Pages workflow`" in roadmap
