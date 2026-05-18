from ticktask.mcp import resources
from ticktask.mcp.server import build_server


class LockedKeyring:
    def get_password(self, service_name: str, username: str) -> str | None:
        raise RuntimeError("backend locked")

    def set_password(self, service_name: str, username: str, password: str) -> None:
        raise RuntimeError("backend locked")

    def delete_password(self, service_name: str, username: str) -> None:
        raise RuntimeError("backend locked")


class FakeService:
    def list_projects(self):
        return [
            {"id": "p1", "name": "Inbox"},
            {"id": "p2", "name": "Deep Work"},
        ]


def test_projects_resource_returns_stable_agent_context(monkeypatch) -> None:
    monkeypatch.setattr(resources, "_make_service", lambda: FakeService())

    payload = resources.ticktask_projects_resource()

    assert payload["ok"] is True
    assert payload["uri"] == "ticktask://projects"
    assert payload["data"][0]["id"] == "p1"
    assert payload["meta"]["count"] == 2
    assert payload["meta"]["read_only"] is True


def test_config_resource_sanitizes_secret_fields(monkeypatch, tmp_path) -> None:
    config_path = tmp_path / "config.json"
    config_path.write_text(
        """{
  "active_service": "dida365",
  "profiles": {
    "dida365": {
      "service": "dida365",
      "base_url": "https://api.dida365.com",
      "oauth_authorize_base_url": "https://dida365.com",
      "oauth_token_base_url": "https://api.dida365.com",
      "client_id": "client",
      "client_secret": "secret",
      "redirect_uri": "http://localhost/callback",
      "access_token": "access",
      "refresh_token": "refresh",
      "expires_at": "2026-05-17T00:00:00Z",
      "oauth_state": "state",
      "code_verifier": "verifier"
    }
  }
}
""",
        encoding="utf-8",
    )
    monkeypatch.setenv("TICKTASK_CONFIG_DIR", str(tmp_path))

    payload = resources.ticktask_config_resource()

    profile = payload["data"]["profiles"]["dida365"]
    assert payload["ok"] is True
    assert payload["uri"] == "ticktask://config"
    assert payload["data"]["active_service"] == "dida365"
    assert profile["client_id"] == "client"
    assert profile["client_secret_configured"] is True
    assert profile["access_token_configured"] is True
    assert profile["refresh_token_configured"] is True
    assert "client_secret" not in profile
    assert "access_token" not in profile
    assert "refresh_token" not in profile
    assert "code_verifier" not in profile


def test_config_resource_handles_unavailable_keyring_backend(monkeypatch, tmp_path) -> None:
    config_path = tmp_path / "config.json"
    config_path.write_text(
        """{
  "active_service": "dida365",
  "profiles": {
    "dida365": {
      "service": "dida365",
      "base_url": "https://api.dida365.com",
      "oauth_authorize_base_url": "https://dida365.com",
      "oauth_token_base_url": "https://api.dida365.com",
      "client_id": "client",
      "redirect_uri": "http://localhost/callback",
      "token_storage": "keyring"
    }
  }
}
""",
        encoding="utf-8",
    )
    monkeypatch.setenv("TICKTASK_CONFIG_DIR", str(tmp_path))
    monkeypatch.setattr(
        "ticktask.core.credentials.KeyringCredentialStore._load_backend",
        staticmethod(lambda: LockedKeyring()),
    )

    payload = resources.ticktask_config_resource()

    profile = payload["data"]["profiles"]["dida365"]
    assert payload["ok"] is True
    assert profile["token_storage"] == "keyring"
    assert profile["client_secret_configured"] is False
    assert profile["access_token_configured"] is False
    assert profile["refresh_token_configured"] is False


def test_saved_views_resource_documents_smart_filters() -> None:
    payload = resources.ticktask_saved_views_resource()

    ids = {view["id"] for view in payload["data"]}
    assert payload["ok"] is True
    assert payload["uri"] == "ticktask://saved-views"
    assert {"today", "overdue", "upcoming", "high-priority", "no-date"}.issubset(ids)
    assert all(view["mcp_tool"] == "ticktask_list_tasks" for view in payload["data"])
    assert all("filter_preset" in view["arguments"] for view in payload["data"])


def test_build_server_registers_static_resources() -> None:
    server = build_server()
    resource_uris = {str(resource.uri) for resource in server._resource_manager.list_resources()}

    assert "ticktask://projects" in resource_uris
    assert "ticktask://config" in resource_uris
    assert "ticktask://saved-views" in resource_uris
