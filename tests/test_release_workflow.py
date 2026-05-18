from pathlib import Path


PUBLISH_WORKFLOW = Path(".github/workflows/publish.yml")
RELEASE_DOC = Path("docs/release.md")
INSTALL_DOC = Path("docs/installation.md")
README = Path("README.md")
README_ZH = Path("README.zh-CN.md")
ROADMAP = Path("docs/roadmap.md")


def test_publish_workflow_uses_trusted_publishing_for_pypi_and_testpypi() -> None:
    workflow = PUBLISH_WORKFLOW.read_text()

    assert "name: Publish Python Package" in workflow
    assert "release:" in workflow
    assert "types: [published]" in workflow
    assert "workflow_dispatch:" in workflow
    assert "id-token: write" in workflow
    assert "contents: read" in workflow
    assert "uv build" in workflow
    assert "pypa/gh-action-pypi-publish@release/v1" in workflow
    assert "environment: pypi" in workflow
    assert "environment: testpypi" in workflow
    assert "repository-url: https://test.pypi.org/legacy/" in workflow


def test_release_docs_explain_tagged_release_and_trusted_publishing() -> None:
    release = RELEASE_DOC.read_text()

    assert "Trusted Publishing" in release
    assert "gh release create v0.1.0" in release
    assert "workflow_dispatch" in release
    assert "TestPyPI" in release
    assert "PyPI" in release
    assert "twine check dist/*" in release


def test_install_docs_explain_github_source_now_and_pypi_after_publication() -> None:
    installation = INSTALL_DOC.read_text()
    readme = README.read_text()
    readme_zh = README_ZH.read_text()

    for text in (installation, readme, readme_zh):
        assert "git+https://github.com/GeekMai90/ticktick-mcp-cli.git" in text
        assert (
            "not available on PyPI" in text
            or "not installable from PyPI" in text
            or "还没有发布 `ticktick-mcp-cli`" in text
            or "正式发布后" in text
        )
        assert "uv tool install ticktick-mcp-cli" in text
        assert "pipx install ticktick-mcp-cli" in text
        assert "ticktick-mcp-cli[mcp]" in text


def test_roadmap_marks_pypi_publish_workflow_complete() -> None:
    roadmap = ROADMAP.read_text()

    assert "[x] PyPI publishing workflow" in roadmap
    assert "✅ `feat(dx): add PyPI publish workflow and install docs`" in roadmap
