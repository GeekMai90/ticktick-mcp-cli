from ticktask.core.auth import AuthManager
from ticktask.core.config import ConfigStore


def test_auth_init_and_status(tmp_path) -> None:
    manager = AuthManager(ConfigStore(tmp_path / "config.json"))
    manager.init(
        service="ticktick",
        client_id="client",
        client_secret="secret",
        redirect_uri="http://localhost/callback",
        access_token="token",
    )

    status = manager.status()
    assert status.service == "ticktick"
    assert status.configured is True
    assert status.authenticated is True
    assert status.client_id == "client"


def test_auth_status_without_config_is_not_authenticated(tmp_path) -> None:
    status = AuthManager(ConfigStore(tmp_path / "missing.json")).status()
    assert status.configured is False
    assert status.authenticated is False
