from __future__ import annotations

import typer

from ticktask.cli.formatters import emit_error, emit_result
from ticktask.core.auth import AuthManager

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
