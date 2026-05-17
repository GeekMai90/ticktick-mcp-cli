from pathlib import Path
import tomllib


def test_distribution_name_and_public_console_aliases():
    data = tomllib.loads(Path("pyproject.toml").read_text())

    assert data["project"]["name"] == "ticktick-mcp-cli"
    assert data["project"]["urls"]["Homepage"] == "https://github.com/GeekMai90/ticktick-mcp-cli"

    scripts = data["project"]["scripts"]
    assert scripts["ticktick-mcp-cli"] == "ticktask.cli.app:app"
    assert scripts["ticktick-mcp"] == "ticktask.mcp.server:main"

    # Backward-compatible legacy commands remain available during the rename.
    assert scripts["ticktask"] == "ticktask.cli.app:app"
    assert scripts["tt"] == "ticktask.cli.app:app"
    assert scripts["ticktask-mcp"] == "ticktask.mcp.server:main"
