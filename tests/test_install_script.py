import os
import subprocess
from pathlib import Path


INSTALL_SCRIPT = Path("scripts/install.sh")
INSTALLATION_DOC = Path("docs/installation.md")
README = Path("README.md")
README_ZH = Path("README.zh-CN.md")
ROADMAP = Path("docs/roadmap.md")


def _fake_executable(path: Path, name: str) -> None:
    executable = path / name
    executable.write_text("#!/usr/bin/env sh\nexit 0\n")
    executable.chmod(0o755)


def _run_install_dry_run(tmp_path: Path, *, fake_bins: tuple[str, ...] = ()) -> subprocess.CompletedProcess[str]:
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    for name in fake_bins:
        _fake_executable(bin_dir, name)
    env = {
        **os.environ,
        "PATH": str(bin_dir),
        "TICKTASK_INSTALL_DRY_RUN": "1",
    }
    return subprocess.run(
        ["/bin/sh", str(INSTALL_SCRIPT)],
        text=True,
        capture_output=True,
        check=False,
        env=env,
    )


def test_install_script_prefers_uv_tool_with_mcp_extra(tmp_path: Path) -> None:
    result = _run_install_dry_run(tmp_path, fake_bins=("uv", "pipx", "python3"))

    assert result.returncode == 0
    assert "uv tool install 'ticktick-mcp-cli[mcp,keyring] @ git+https://github.com/GeekMai90/ticktick-mcp-cli.git'" in result.stdout
    assert "ticktick-mcp-cli doctor --json" in result.stdout
    assert "ticktick-mcp-cli auth status --json" in result.stdout


def test_install_script_falls_back_to_pipx_when_uv_is_unavailable(tmp_path: Path) -> None:
    result = _run_install_dry_run(tmp_path, fake_bins=("pipx", "python3"))

    assert result.returncode == 0
    assert "pipx install 'ticktick-mcp-cli[mcp,keyring] @ git+https://github.com/GeekMai90/ticktick-mcp-cli.git'" in result.stdout


def test_install_script_exits_with_hint_when_no_supported_installer_exists(tmp_path: Path) -> None:
    result = _run_install_dry_run(tmp_path)

    assert result.returncode == 1
    assert "Install uv or pipx" in result.stderr


def test_install_docs_reference_script_and_verification_commands() -> None:
    installation = INSTALLATION_DOC.read_text()
    readme = README.read_text()
    readme_zh = README_ZH.read_text()

    for text in (installation, readme, readme_zh):
        assert "curl -fsSL https://raw.githubusercontent.com/GeekMai90/ticktick-mcp-cli/main/scripts/install.sh | sh" in text
        assert "ticktick-mcp-cli doctor --json" in text
        assert "ticktick-mcp-cli auth status --json" in text
        assert "git+https://github.com/GeekMai90/ticktick-mcp-cli.git" in text


def test_roadmap_marks_install_script_complete_and_omits_homebrew_channel() -> None:
    roadmap = ROADMAP.read_text()

    assert "[x] Installer script for uv/pipx" in roadmap
    assert "Homebrew" not in roadmap
    assert "✅ `feat(dx): add installer script`" in roadmap
