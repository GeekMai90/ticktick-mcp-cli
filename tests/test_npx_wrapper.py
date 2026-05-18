import json
import os
import shutil
import subprocess
from pathlib import Path


PACKAGE_JSON = Path("package.json")
NPX_WRAPPER = Path("scripts/npx-wrapper.js")
README = Path("README.md")
README_ZH = Path("README.zh-CN.md")
INSTALLATION_DOC = Path("docs/installation.md")
ROADMAP = Path("docs/roadmap.md")


def _fake_executable(path: Path, name: str) -> None:
    executable = path / name
    executable.write_text("#!/usr/bin/env sh\nexit 0\n")
    executable.chmod(0o755)


def _run_wrapper_dry_run(
    tmp_path: Path,
    *,
    fake_bins: tuple[str, ...],
    args: list[str] | None = None,
    script: Path = NPX_WRAPPER,
) -> subprocess.CompletedProcess[str]:
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    for name in fake_bins:
        _fake_executable(bin_dir, name)
    env = {
        **os.environ,
        "PATH": str(bin_dir),
        "TICKTASK_NPX_DRY_RUN": "1",
    }
    node = shutil.which("node")
    assert node is not None
    return subprocess.run(
        [node, str(script), *(args or [])],
        text=True,
        capture_output=True,
        check=False,
        env=env,
    )


def test_package_json_exposes_npx_cli_and_mcp_bins() -> None:
    package = json.loads(PACKAGE_JSON.read_text())

    assert package["name"] == "ticktick-mcp-cli"
    assert package["private"] is False
    assert package["bin"]["ticktick-mcp-cli"] == "scripts/npx-wrapper.js"
    assert package["bin"]["ticktick-mcp"] == "scripts/npx-wrapper.js"
    assert "scripts/npx-wrapper.js" in package["files"]
    assert "scripts/install.sh" in package["files"]


def test_npx_wrapper_prefers_uvx_and_preserves_args(tmp_path: Path) -> None:
    result = _run_wrapper_dry_run(tmp_path, fake_bins=("uvx", "python3"), args=["doctor", "--json"])

    assert result.returncode == 0
    assert "uvx --from ticktick-mcp-cli[mcp,keyring] @ git+https://github.com/GeekMai90/ticktick-mcp-cli.git ticktick-mcp-cli doctor --json" in result.stdout


def test_npx_wrapper_falls_back_to_pipx_run_when_uvx_is_unavailable(tmp_path: Path) -> None:
    result = _run_wrapper_dry_run(tmp_path, fake_bins=("python3",), args=["auth", "status", "--json"])

    assert result.returncode == 0
    assert "python3 -m pipx run --spec ticktick-mcp-cli[mcp,keyring] @ git+https://github.com/GeekMai90/ticktick-mcp-cli.git ticktick-mcp-cli auth status --json" in result.stdout


def test_npx_wrapper_dispatches_mcp_bin_name(tmp_path: Path) -> None:
    mcp_link = tmp_path / "ticktick-mcp"
    mcp_link.symlink_to(Path.cwd() / NPX_WRAPPER)

    result = _run_wrapper_dry_run(tmp_path, fake_bins=("uvx",), script=mcp_link)

    assert result.returncode == 0
    assert "uvx --from ticktick-mcp-cli[mcp,keyring] @ git+https://github.com/GeekMai90/ticktick-mcp-cli.git ticktick-mcp" in result.stdout


def test_npx_wrapper_exits_with_hint_when_no_runner_exists(tmp_path: Path) -> None:
    result = _run_wrapper_dry_run(tmp_path, fake_bins=())

    assert result.returncode == 1
    assert "Install uv/uvx or Python with pipx" in result.stderr


def test_docs_explain_github_npx_agent_install_without_claiming_registry_publish() -> None:
    readme = README.read_text()
    readme_zh = README_ZH.read_text()
    installation = INSTALLATION_DOC.read_text()

    for text in (readme, readme_zh, installation):
        assert "npx github:GeekMai90/ticktick-mcp-cli" in text
        assert "npm install -g ticktick-mcp-cli" not in text
        assert "git+https://github.com/GeekMai90/ticktick-mcp-cli.git" in text


def test_roadmap_marks_npx_wrapper_complete() -> None:
    roadmap = ROADMAP.read_text()

    assert "[x] GitHub npx wrapper for agent installs" in roadmap
    assert "✅ `feat(dx): add npx wrapper for agent installs`" in roadmap
