from __future__ import annotations

import webbrowser

import typer

from ticktask.cli.formatters import emit_error, emit_json, emit_result
from ticktask.core.auth import AuthManager
from ticktask.core.results import ok

app = typer.Typer(help="Configure OAuth credentials and inspect login status.")


@app.command("init")
def auth_init(
    service: str = typer.Option(..., "--service", help="Service profile: ticktick or dida365."),
    client_id: str = typer.Option(..., "--client-id", help="OAuth client ID."),
    client_secret: str = typer.Option(..., "--client-secret", help="OAuth client secret."),
    redirect_uri: str = typer.Option(..., "--redirect-uri", help="OAuth redirect URI."),
    access_token: str | None = typer.Option(
        None,
        "--access-token",
        help="Optional existing access token for local testing.",
    ),
    refresh_token: str | None = typer.Option(None, "--refresh-token", help="Optional refresh token."),
    json_output: bool = typer.Option(False, "--json", help="Emit stable JSON."),
) -> None:
    try:
        manager = AuthManager()
        profile = manager.init(
            service=service,
            client_id=client_id,
            client_secret=client_secret,
            redirect_uri=redirect_uri,
            access_token=access_token,
            refresh_token=refresh_token,
        )
        emit_result(
            {
                "service": profile.service,
                "base_url": profile.base_url,
                "configured": profile.is_configured(),
                "authenticated": profile.has_token(),
                "config_path": manager.store.path_string(),
            },
            json_output=json_output,
        )
    except Exception as exc:
        emit_error(exc, json_output)


@app.command("status")
def auth_status(
    service: str | None = typer.Option(None, "--service", help="Service profile to inspect."),
    json_output: bool = typer.Option(False, "--json", help="Emit stable JSON."),
) -> None:
    try:
        status = AuthManager().status(service)
        emit_result(status.to_dict(), json_output=json_output)
    except Exception as exc:
        emit_error(exc, json_output)


@app.command("login")
def auth_login(
    service: str | None = typer.Option(None, "--service", help="Service profile: ticktick or dida365."),
    no_browser: bool = typer.Option(False, "--no-browser", help="Print the authorization URL instead of opening it."),
    code: str | None = typer.Option(
        None,
        "--code",
        help="OAuth callback code. Useful for non-browser and testable local flows.",
    ),
    callback_url: str | None = typer.Option(
        None,
        "--callback-url",
        help="Full OAuth callback URL. Extracts code and validates the stored state.",
    ),
    state: str | None = typer.Option(
        None,
        "--state",
        help="OAuth state printed by `auth login --no-browser`; used with --code.",
    ),
    json_output: bool = typer.Option(False, "--json", help="Emit stable JSON."),
) -> None:
    try:
        manager = AuthManager()
        if callback_url:
            callback = manager.parse_callback_url(callback_url, service)
            code = callback["code"]
            state = callback.get("state") or None
        if code:
            profile = manager.login_with_code(code, service, state=state)
            data = {
                "service": profile.service,
                "authenticated": profile.has_token(),
                "has_refresh_token": bool(profile.refresh_token),
                "expires_at": profile.expires_at,
            }
            emit_result(data, json_output=json_output)
            return

        flow = manager.begin_login(service)
        authorization_url = flow.authorization_url
        if not no_browser:
            webbrowser.open(authorization_url)
        data = {
            "authorization_url": authorization_url,
            "state": flow.state,
            "authenticated": False,
            "next": "Open the URL, copy the callback code, then run `ticktask auth login --code CODE`.",
        }
        if json_output:
            emit_json(ok(data))
        else:
            typer.echo(authorization_url)
            typer.echo(data["next"])
    except Exception as exc:
        emit_error(exc, json_output)


@app.command("refresh")
def auth_refresh(
    service: str | None = typer.Option(None, "--service", help="Service profile: ticktick or dida365."),
    json_output: bool = typer.Option(False, "--json", help="Emit stable JSON."),
) -> None:
    try:
        profile = AuthManager().refresh(service)
        emit_result(
            {
                "service": profile.service,
                "authenticated": profile.has_token(),
                "has_refresh_token": bool(profile.refresh_token),
                "expires_at": profile.expires_at,
            },
            json_output=json_output,
        )
    except Exception as exc:
        emit_error(exc, json_output)
