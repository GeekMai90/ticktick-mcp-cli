from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import UTC, datetime, timedelta
import base64
import hashlib
import secrets
from typing import Any
from urllib.parse import parse_qs, urlencode, urlparse

import httpx

from ticktask.core.client import request_json_without_auth
from ticktask.core.config import ConfigStore, ProfileConfig
from ticktask.core.credentials import credential_store_for
from ticktask.core.errors import AuthError, ConfigError


@dataclass
class AuthStatus:
    service: str
    base_url: str
    config_path: str
    configured: bool
    authenticated: bool
    has_refresh_token: bool
    client_id: str | None
    redirect_uri: str | None
    expires_at: str | None
    token_storage: str
    keyring_available: bool | None = None
    keyring_hint: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class AuthorizationFlow:
    authorization_url: str
    state: str
    code_verifier: str
    code_challenge: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class AuthManager:
    def __init__(self, store: ConfigStore | None = None) -> None:
        self.store = store or ConfigStore()

    def init(
        self,
        service: str,
        client_id: str,
        client_secret: str,
        redirect_uri: str,
        access_token: str | None = None,
        refresh_token: str | None = None,
        expires_at: str | None = None,
        token_storage: str = "file",
    ) -> ProfileConfig:
        profile = ProfileConfig.for_service(
            service=service,
            client_id=client_id,
            client_secret=client_secret,
            redirect_uri=redirect_uri,
            token_storage=token_storage,
        )
        profile.access_token = access_token
        profile.refresh_token = refresh_token
        profile.expires_at = expires_at
        profile.save_external_credentials()
        config = self.store.load()
        config.set_profile(profile)
        self.store.save(config)
        return profile

    def status(self, service: str | None = None) -> AuthStatus:
        config = self.store.load()
        try:
            profile = config.get_profile(service)
        except ConfigError:
            service_name = service or config.active_service
            from ticktask.core.constants import get_service_profile

            service_profile = get_service_profile(service_name)
            return AuthStatus(
                service=service_profile.name,
                base_url=service_profile.base_url,
                config_path=self.store.path_string(),
                configured=False,
                authenticated=False,
                has_refresh_token=False,
                client_id=None,
                redirect_uri=None,
                expires_at=None,
                token_storage="file",
            )
        backend_status = self._credential_backend_status(profile)
        if profile.token_storage != "keyring" or backend_status["keyring_available"] is not False:
            try:
                profile = profile.hydrate_credentials()
            except Exception as exc:
                backend_status = {
                    "keyring_available": False,
                    "keyring_hint": f"Keyring backend is unavailable: {exc}",
                }
        return AuthStatus(
            service=profile.service,
            base_url=profile.base_url,
            config_path=self.store.path_string(),
            configured=profile.is_configured(),
            authenticated=profile.has_token(),
            has_refresh_token=bool(profile.refresh_token),
            client_id=profile.client_id,
            redirect_uri=profile.redirect_uri,
            expires_at=profile.expires_at,
            token_storage=profile.token_storage,
            **backend_status,
        )

    def authorization_url(
        self,
        service: str | None = None,
        scope: str | None = None,
        state: str | None = None,
        code_challenge: str | None = None,
    ) -> str:
        profile = self._require_configured_profile(service)
        params = {
            "client_id": profile.client_id or "",
            "redirect_uri": profile.redirect_uri or "",
            "response_type": "code",
        }
        if scope:
            params["scope"] = scope
        if state:
            params["state"] = state
        if code_challenge:
            params["code_challenge"] = code_challenge
            params["code_challenge_method"] = "S256"
        authorize_base_url = profile.oauth_authorize_base_url.rstrip("/")
        return f"{authorize_base_url}/oauth/authorize?{urlencode(params)}"

    def begin_login(self, service: str | None = None, scope: str | None = None) -> AuthorizationFlow:
        profile = self._require_configured_profile(service)
        state = secrets.token_urlsafe(32)
        code_verifier = secrets.token_urlsafe(64)
        code_challenge = _pkce_challenge(code_verifier)
        profile.oauth_state = state
        profile.code_verifier = code_verifier
        config = self.store.load()
        profile.save_external_credentials()
        config.set_profile(profile)
        self.store.save(config)
        return AuthorizationFlow(
            authorization_url=self.authorization_url(
                service=profile.service,
                scope=scope,
                state=state,
                code_challenge=code_challenge,
            ),
            state=state,
            code_verifier=code_verifier,
            code_challenge=code_challenge,
        )

    def parse_callback_url(self, callback_url: str, service: str | None = None) -> dict[str, str]:
        profile = self._require_configured_profile(service)
        query = parse_qs(urlparse(callback_url).query)
        code = _first_query_value(query, "code")
        state = _first_query_value(query, "state")
        error = _first_query_value(query, "error")
        if error:
            raise AuthError(f"OAuth callback returned error: {error}")
        if not code:
            raise AuthError("OAuth callback URL did not include a code.")
        self._validate_state(profile, state)
        return {"code": code, "state": state or ""}

    def login_with_code(
        self,
        code: str,
        service: str | None = None,
        http_client: httpx.Client | None = None,
        state: str | None = None,
    ) -> ProfileConfig:
        profile = self._require_configured_profile(service)
        self._validate_state(profile, state)
        payload = {
            "grant_type": "authorization_code",
            "code": code,
            "client_id": profile.client_id,
            "client_secret": profile.client_secret,
            "redirect_uri": profile.redirect_uri,
        }
        if profile.code_verifier:
            payload["code_verifier"] = profile.code_verifier
        token_payload = request_json_without_auth(
            profile.oauth_token_base_url,
            "POST",
            "/oauth/token",
            data=payload,
            http_client=http_client,
        )
        return self._store_tokens(profile, token_payload)

    def refresh(
        self,
        service: str | None = None,
        http_client: httpx.Client | None = None,
    ) -> ProfileConfig:
        profile = self._require_configured_profile(service)
        if not profile.refresh_token:
            raise AuthError(
                f"Service profile `{profile.service}` has no refresh token.",
                hint="Run `ticktask auth login` to obtain a refresh token first.",
            )
        payload = {
            "grant_type": "refresh_token",
            "refresh_token": profile.refresh_token,
            "client_id": profile.client_id,
            "client_secret": profile.client_secret,
        }
        token_payload = request_json_without_auth(
            profile.oauth_token_base_url,
            "POST",
            "/oauth/token",
            data=payload,
            http_client=http_client,
        )
        return self._store_tokens(profile, token_payload)

    def require_token(
        self,
        service: str | None = None,
        http_client: httpx.Client | None = None,
    ) -> ProfileConfig:
        config = self.store.load()
        profile = config.get_profile(service).hydrate_credentials()
        if not profile.access_token:
            raise AuthError(
                f"Service profile `{profile.service}` has no access token.",
                hint=(
                    "Run `ticktask auth init ... --access-token TOKEN` for testing or complete "
                    "the OAuth browser flow when it is configured."
                ),
            )
        if self._should_refresh(profile):
            if not profile.refresh_token:
                raise AuthError(
                    f"Service profile `{profile.service}` access token is expired and has no refresh token.",
                    hint="Run `ticktask auth login` to obtain a fresh access token.",
                )
            return self.refresh(profile.service, http_client=http_client)
        return profile

    def _require_configured_profile(self, service: str | None = None) -> ProfileConfig:
        config = self.store.load()
        profile = config.get_profile(service).hydrate_credentials()
        if not profile.is_configured():
            raise AuthError(
                f"Service profile `{profile.service}` is missing OAuth client config.",
                hint="Run `ticktask auth init --service SERVICE --client-id ... --client-secret ... --redirect-uri ...`.",
            )
        return profile

    @staticmethod
    def _credential_backend_status(profile: ProfileConfig) -> dict[str, Any]:
        if profile.token_storage != "keyring":
            return {"keyring_available": None, "keyring_hint": None}
        try:
            status = credential_store_for(profile.token_storage).status()
        except ConfigError as exc:
            return {"keyring_available": False, "keyring_hint": str(exc)}
        return {"keyring_available": status.available, "keyring_hint": status.hint}

    @staticmethod
    def _should_refresh(profile: ProfileConfig, skew: timedelta = timedelta(minutes=5)) -> bool:
        if not profile.expires_at:
            return False
        try:
            expires_at = datetime.fromisoformat(profile.expires_at)
        except ValueError:
            return True
        if expires_at.tzinfo is None:
            expires_at = expires_at.replace(tzinfo=UTC)
        return expires_at <= datetime.now(UTC) + skew

    @staticmethod
    def _validate_state(profile: ProfileConfig, state: str | None) -> None:
        if profile.oauth_state and state != profile.oauth_state:
            raise AuthError("OAuth callback state did not match the stored login state.")

    def _store_tokens(self, profile: ProfileConfig, token_payload: dict[str, Any]) -> ProfileConfig:
        access_token = token_payload.get("access_token")
        if not access_token:
            raise AuthError("OAuth token response did not include an access_token.")
        profile.access_token = str(access_token)
        refresh_token = token_payload.get("refresh_token")
        if refresh_token:
            profile.refresh_token = str(refresh_token)
        profile.oauth_state = None
        profile.code_verifier = None
        expires_in = token_payload.get("expires_in")
        if expires_in is not None:
            try:
                expires_at = datetime.now(UTC) + timedelta(seconds=int(expires_in))
            except (TypeError, ValueError) as exc:
                raise AuthError("OAuth token response included an invalid expires_in value.") from exc
            profile.expires_at = expires_at.isoformat()
        config = self.store.load()
        profile.save_external_credentials()
        config.set_profile(profile)
        self.store.save(config)
        return profile


def _pkce_challenge(code_verifier: str) -> str:
    digest = hashlib.sha256(code_verifier.encode("ascii")).digest()
    return base64.urlsafe_b64encode(digest).decode("ascii").rstrip("=")


def _first_query_value(query: dict[str, list[str]], key: str) -> str | None:
    values = query.get(key)
    if not values:
        return None
    return values[0]
