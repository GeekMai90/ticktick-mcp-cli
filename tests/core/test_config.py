from ticktask.core.config import ConfigStore, ProfileConfig, config_path
from ticktask.core.constants import get_service_profile


def test_service_profiles() -> None:
    assert get_service_profile("ticktick").base_url == "https://api.ticktick.com"
    assert get_service_profile("dida365").base_url == "https://api.dida365.com"


def test_config_path_uses_env(tmp_path, monkeypatch) -> None:
    monkeypatch.setenv("TICKTASK_CONFIG_DIR", str(tmp_path))
    assert config_path() == tmp_path / "config.json"


def test_config_roundtrip(tmp_path) -> None:
    store = ConfigStore(tmp_path / "config.json")
    config = store.load()
    config.set_profile(
        ProfileConfig.for_service("dida365", "client", "secret", "http://localhost/callback")
    )
    store.save(config)

    loaded = store.load()
    profile = loaded.get_profile("dida365")
    assert loaded.active_service == "dida365"
    assert profile.base_url == "https://api.dida365.com"
    assert profile.client_id == "client"
