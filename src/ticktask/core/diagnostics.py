from __future__ import annotations

import json
import platform
import sys
import zipfile
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from ticktask import __version__
from ticktask.core.auth import AuthManager
from ticktask.core.config import ConfigStore, ProfileConfig

_SECRET_KEYS = {
    "access_token",
    "refresh_token",
    "client_secret",
    "oauth_state",
    "code_verifier",
    "authorization",
    "token",
    "secret",
}


def redact_mapping(value: Any) -> Any:
    """Recursively redact secret-looking mapping values while preserving safe fields."""
    if isinstance(value, dict):
        redacted: dict[str, Any] = {}
        for key, item in value.items():
            if _is_secret_key(str(key)):
                redacted[key] = "<redacted>" if item else None
            else:
                redacted[key] = redact_mapping(item)
        return redacted
    if isinstance(value, list):
        return [redact_mapping(item) for item in value]
    return value


def collect_diagnostics(store: ConfigStore | None = None) -> dict[str, Any]:
    """Collect a redacted, no-network diagnostic snapshot for support and agent handoff."""
    config_store = store or ConfigStore()
    config = config_store.load()
    status = AuthManager(config_store).status()
    data = {
        "version": __version__,
        "generated_at": datetime.now(UTC).isoformat(),
        "python": {
            "version": sys.version.split()[0],
            "implementation": platform.python_implementation(),
            "platform": platform.platform(),
        },
        "environment": {
            "ticktask_config_dir_set": "TICKTASK_CONFIG_DIR" in __import__("os").environ,
        },
        "config": {
            "path": config_store.path_string(),
            "exists": config_store.path.exists(),
            "active_service": config.active_service,
            "profiles": {
                service: _sanitize_profile(profile) for service, profile in config.profiles.items()
            },
        },
        "auth": {
            "service": status.service,
            "base_url": status.base_url,
            "configured": status.configured,
            "authenticated": status.authenticated,
            "has_refresh_token": status.has_refresh_token,
            "client_id_configured": bool(status.client_id),
            "redirect_uri_configured": bool(status.redirect_uri),
            "expires_at_configured": bool(status.expires_at),
        },
        "mcp": _mcp_status(),
        "tools": _tool_status(),
    }
    return redact_mapping(data)


def create_diagnostic_bundle(
    output_path: str | Path,
    store: ConfigStore | None = None,
) -> dict[str, Any]:
    """Write a redacted diagnostic ZIP bundle and return its manifest."""
    path = Path(output_path).expanduser()
    path.parent.mkdir(parents=True, exist_ok=True)
    diagnostics = collect_diagnostics(store=store)
    report = _render_report(diagnostics)
    files = [
        {"path": "diagnostics.json", "description": "Redacted machine-readable diagnostic snapshot."},
        {"path": "report.md", "description": "Human-readable support summary."},
    ]
    with zipfile.ZipFile(path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        archive.writestr("diagnostics.json", json.dumps(diagnostics, indent=2, sort_keys=True) + "\n")
        archive.writestr("report.md", report)
    return {
        "bundle_path": str(path),
        "redacted": True,
        "files": files,
        "generated_at": diagnostics["generated_at"],
    }


def _sanitize_profile(profile: ProfileConfig) -> dict[str, Any]:
    return {
        "service": profile.service,
        "base_url": profile.base_url,
        "oauth_authorize_base_url": profile.oauth_authorize_base_url,
        "oauth_token_base_url": profile.oauth_token_base_url,
        "client_id_configured": bool(profile.client_id),
        "client_secret_configured": bool(profile.client_secret),
        "redirect_uri_configured": bool(profile.redirect_uri),
        "access_token_configured": bool(profile.access_token),
        "refresh_token_configured": bool(profile.refresh_token),
        "expires_at_configured": bool(profile.expires_at),
        "oauth_state_configured": bool(profile.oauth_state),
        "code_verifier_configured": bool(profile.code_verifier),
    }


def _is_secret_key(key: str) -> bool:
    normalized = key.casefold()
    if normalized in {"client_id", "redirect_uri"} or normalized.endswith("_configured"):
        return False
    return any(marker in normalized for marker in _SECRET_KEYS)


def _mcp_status() -> dict[str, Any]:
    try:
        from ticktask.mcp.server import build_server

        build_server()
    except Exception as exc:  # pragma: no cover - depends on optional runtime
        return {"server_buildable": False, "error": type(exc).__name__}
    return {"server_buildable": True, "error": None}


def _tool_status() -> dict[str, Any]:
    try:
        from ticktask.mcp import tools

        definitions = tools.ticktask_describe_tools()["data"]
        return {
            "mcp_tool_count": len(definitions),
            "cli_aliases": ["ticktask", "tt", "ticktick-mcp-cli"],
            "mcp_aliases": ["ticktask-mcp", "ticktick-mcp"],
        }
    except Exception as exc:  # pragma: no cover - defensive support path
        return {
            "mcp_tool_count": 0,
            "cli_aliases": ["ticktask", "tt", "ticktick-mcp-cli"],
            "mcp_aliases": ["ticktask-mcp", "ticktick-mcp"],
            "error": type(exc).__name__,
        }


def _render_report(diagnostics: dict[str, Any]) -> str:
    auth = diagnostics["auth"]
    config = diagnostics["config"]
    mcp = diagnostics["mcp"]
    tools = diagnostics["tools"]
    return (
        "# Ticktask Redacted Diagnostic Bundle\n\n"
        f"- Version: `{diagnostics['version']}`\n"
        f"- Generated at: `{diagnostics['generated_at']}`\n"
        f"- Python: `{diagnostics['python']['version']}` on `{diagnostics['python']['platform']}`\n"
        f"- Config path: `{config['path']}`\n"
        f"- Config exists: `{config['exists']}`\n"
        f"- Active service: `{config['active_service']}`\n"
        f"- Auth configured: `{auth['configured']}`\n"
        f"- Authenticated: `{auth['authenticated']}`\n"
        f"- Refresh token configured: `{auth['has_refresh_token']}`\n"
        f"- MCP server buildable: `{mcp['server_buildable']}`\n"
        f"- MCP tool count: `{tools['mcp_tool_count']}`\n\n"
        "Secrets are intentionally redacted. Share this bundle in bug reports instead of raw config files.\n"
    )
