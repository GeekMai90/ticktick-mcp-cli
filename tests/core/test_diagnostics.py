import json
import zipfile

from ticktask.core.config import ConfigStore, ProfileConfig
from ticktask.core.diagnostics import collect_diagnostics, create_diagnostic_bundle, redact_mapping


def _configured_store(tmp_path):
    store = ConfigStore(tmp_path / "config.json")
    config = store.load()
    profile = ProfileConfig.for_service("dida365", "client-id", "client-secret", "http://localhost/callback")
    profile.access_token = "access-token-secret"
    profile.refresh_token = "refresh-token-secret"
    profile.oauth_state = "oauth-state-secret"
    profile.code_verifier = "code-verifier-secret"
    profile.expires_at = "2099-01-01T00:00:00Z"
    config.set_profile(profile)
    store.save(config)
    return store


def test_redact_mapping_replaces_secret_values() -> None:
    payload = {
        "client_id": "public-client",
        "client_secret": "secret-value",
        "nested": {"access_token": "token-value", "safe": "ok"},
    }

    redacted = redact_mapping(payload)

    assert redacted["client_id"] == "public-client"
    assert redacted["client_secret"] == "<redacted>"
    assert redacted["nested"]["access_token"] == "<redacted>"
    assert redacted["nested"]["safe"] == "ok"


def test_collect_diagnostics_sanitizes_config_and_reports_runtime(tmp_path) -> None:
    store = _configured_store(tmp_path)

    data = collect_diagnostics(store=store)
    serialized = json.dumps(data)

    assert data["version"]
    assert data["python"]["version"]
    assert data["config"]["path"] == store.path_string()
    assert data["config"]["exists"] is True
    assert data["config"]["active_service"] == "dida365"
    profile = data["config"]["profiles"]["dida365"]
    assert profile["client_id_configured"] is True
    assert profile["client_secret_configured"] is True
    assert profile["access_token_configured"] is True
    assert "client-secret" not in serialized
    assert "access-token-secret" not in serialized
    assert "refresh-token-secret" not in serialized
    assert data["mcp"]["server_buildable"] is True
    assert data["tools"]["mcp_tool_count"] > 0


def test_create_diagnostic_bundle_writes_redacted_zip_and_report(tmp_path) -> None:
    store = _configured_store(tmp_path)
    output_path = tmp_path / "diagnostics.zip"

    result = create_diagnostic_bundle(output_path=output_path, store=store)

    assert result["bundle_path"] == str(output_path)
    assert result["redacted"] is True
    assert {item["path"] for item in result["files"]} == {"diagnostics.json", "report.md"}
    with zipfile.ZipFile(output_path) as archive:
        names = set(archive.namelist())
        diagnostics = json.loads(archive.read("diagnostics.json"))
        report = archive.read("report.md").decode("utf-8")
    assert names == {"diagnostics.json", "report.md"}
    assert diagnostics["config"]["profiles"]["dida365"]["refresh_token_configured"] is True
    assert "client-secret" not in json.dumps(diagnostics)
    assert "access-token-secret" not in report
    assert "Redacted Diagnostic Bundle" in report
