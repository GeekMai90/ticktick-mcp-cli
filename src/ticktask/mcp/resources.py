from __future__ import annotations

from dataclasses import asdict
from typing import Any

from ticktask.core.config import ConfigStore, ProfileConfig
from ticktask.core.results import err, ok
from ticktask.core.services import TicktaskService


def _make_service() -> TicktaskService:
    return TicktaskService()


def ticktask_projects_resource() -> dict[str, Any]:
    """Return read-only project context for agent planning."""
    try:
        projects = _make_service().list_projects()
        payload = ok(projects, {"count": len(projects), "read_only": True})
        payload["uri"] = "ticktask://projects"
        return payload
    except Exception as exc:
        payload = err(exc)
        payload["uri"] = "ticktask://projects"
        return payload


def ticktask_config_resource() -> dict[str, Any]:
    """Return sanitized local Ticktask configuration without secrets."""
    uri = "ticktask://config"
    try:
        store = ConfigStore()
        config = store.load()
        data = {
            "active_service": config.active_service,
            "config_path": store.path_string(),
            "profiles": {
                service: _sanitize_profile(profile)
                for service, profile in config.profiles.items()
            },
        }
        payload = ok(data, {"read_only": True, "secret_fields_redacted": True})
        payload["uri"] = uri
        return payload
    except Exception as exc:
        payload = err(exc)
        payload["uri"] = uri
        return payload


def ticktask_saved_views_resource() -> dict[str, Any]:
    """Return built-in smart-filter views as agent-readable resource metadata."""
    uri = "ticktask://saved-views"
    views = [
        {
            "id": "today",
            "name": "Today",
            "description": "Open tasks due today.",
            "mcp_tool": "ticktask_list_tasks",
            "cli_command": "ticktask task list --filter-preset today --json",
            "arguments": {"status": "open", "filter_preset": "today"},
        },
        {
            "id": "overdue",
            "name": "Overdue",
            "description": "Open tasks with due dates before today.",
            "mcp_tool": "ticktask_list_tasks",
            "cli_command": "ticktask task list --filter-preset overdue --json",
            "arguments": {"status": "open", "filter_preset": "overdue"},
        },
        {
            "id": "upcoming",
            "name": "Upcoming",
            "description": "Open tasks with future due dates.",
            "mcp_tool": "ticktask_list_tasks",
            "cli_command": "ticktask task list --filter-preset upcoming --json",
            "arguments": {"status": "open", "filter_preset": "upcoming"},
        },
        {
            "id": "high-priority",
            "name": "High Priority",
            "description": "Open high-priority tasks.",
            "mcp_tool": "ticktask_list_tasks",
            "cli_command": "ticktask task list --filter-preset high-priority --json",
            "arguments": {"status": "open", "filter_preset": "high-priority"},
        },
        {
            "id": "no-date",
            "name": "No Date",
            "description": "Open tasks without a due date.",
            "mcp_tool": "ticktask_list_tasks",
            "cli_command": "ticktask task list --filter-preset no-date --json",
            "arguments": {"status": "open", "filter_preset": "no-date"},
        },
    ]
    payload = ok(views, {"count": len(views), "read_only": True})
    payload["uri"] = uri
    return payload


def _sanitize_profile(profile: ProfileConfig) -> dict[str, Any]:
    raw = asdict(profile)
    sanitized = {
        key: value
        for key, value in raw.items()
        if key
        not in {
            "client_secret",
            "access_token",
            "refresh_token",
            "oauth_state",
            "code_verifier",
        }
    }
    sanitized["client_secret_configured"] = bool(profile.client_secret)
    sanitized["access_token_configured"] = bool(profile.access_token)
    sanitized["refresh_token_configured"] = bool(profile.refresh_token)
    sanitized["oauth_state_configured"] = bool(profile.oauth_state)
    return sanitized


RESOURCE_DEFINITIONS: dict[str, dict[str, Any]] = {
    "ticktask://projects": {
        "function": ticktask_projects_resource,
        "name": "ticktask_projects",
        "title": "Ticktask Projects",
        "description": "Read-only list of TickTick/Dida365 projects for agent planning.",
        "mime_type": "application/json",
    },
    "ticktask://config": {
        "function": ticktask_config_resource,
        "name": "ticktask_config",
        "title": "Ticktask Config",
        "description": "Sanitized local configuration and active service profile, with secrets redacted.",
        "mime_type": "application/json",
    },
    "ticktask://saved-views": {
        "function": ticktask_saved_views_resource,
        "name": "ticktask_saved_views",
        "title": "Ticktask Saved Views",
        "description": "Built-in smart views and their equivalent MCP/CLI arguments.",
        "mime_type": "application/json",
    },
}
