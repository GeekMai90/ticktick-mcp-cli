from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ServiceProfile:
    name: str
    base_url: str
    oauth_authorize_base_url: str
    oauth_token_base_url: str


SERVICE_PROFILES: dict[str, ServiceProfile] = {
    "ticktick": ServiceProfile(
        "ticktick",
        "https://api.ticktick.com",
        "https://ticktick.com",
        "https://ticktick.com",
    ),
    "dida365": ServiceProfile(
        "dida365",
        "https://api.dida365.com",
        "https://dida365.com",
        "https://dida365.com",
    ),
}

DEFAULT_SERVICE = "ticktick"
CONFIG_FILENAME = "config.json"


def get_service_profile(name: str | None) -> ServiceProfile:
    service_name = name or DEFAULT_SERVICE
    try:
        return SERVICE_PROFILES[service_name]
    except KeyError as exc:
        valid = ", ".join(sorted(SERVICE_PROFILES))
        from ticktask.core.errors import ConfigError

        raise ConfigError(
            f"Unknown service profile: {service_name}",
            hint=f"Use one of: {valid}.",
        ) from exc
