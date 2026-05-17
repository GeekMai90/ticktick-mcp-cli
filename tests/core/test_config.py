from ticktask.core.config import ConfigStore, ProfileConfig, config_path
from ticktask.core.constants import get_service_profile


def test_service_profiles() -> None:
    ticktick = get_service_profile("ticktick")
    dida365 = get_service_profile("dida365")
    assert ticktick.base_url == "https://api.ticktick.com"
    assert ticktick.oauth_authorize_base_url == "https://ticktick.com"
    assert ticktick.oauth_token_base_url == "https://ticktick.com"
    assert dida365.base_url == "https://api.dida365.com"
    assert dida365.oauth_authorize_base_url == "https://dida365.com"
    assert dida365.oauth_token_base_url == "https://dida365.com"


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
    assert profile.oauth_authorize_base_url == "https://dida365.com"
    assert profile.oauth_token_base_url == "https://dida365.com"
    assert profile.client_id == "client"


def test_legacy_config_loads_with_default_oauth_urls() -> None:
    profile = ProfileConfig.from_dict(
        {
            "service": "ticktick",
            "base_url": "https://api.ticktick.com",
            "client_id": "client",
            "client_secret": "secret",
            "redirect_uri": "http://localhost/callback",
        }
    )

    assert profile.base_url == "https://api.ticktick.com"
    assert profile.oauth_authorize_base_url == "https://ticktick.com"
    assert profile.oauth_token_base_url == "https://ticktick.com"


def test_config_save_sets_owner_only_permissions(tmp_path) -> None:
    store = ConfigStore(tmp_path / "config.json")
    store.save(store.load())

    assert store.path.stat().st_mode & 0o777 == 0o600
