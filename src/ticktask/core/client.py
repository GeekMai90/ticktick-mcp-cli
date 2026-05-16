from __future__ import annotations

from typing import Any

import httpx

from ticktask.core.errors import ApiError


class TicktaskClient:
    def __init__(
        self,
        base_url: str,
        access_token: str,
        http_client: httpx.Client | None = None,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.access_token = access_token
        self._owns_client = http_client is None
        self.http = http_client or httpx.Client(timeout=20)

    def close(self) -> None:
        if self._owns_client:
            self.http.close()

    def __enter__(self) -> TicktaskClient:
        return self

    def __exit__(self, *_exc: object) -> None:
        self.close()

    def request(self, method: str, path: str, **kwargs: Any) -> Any:
        url = f"{self.base_url}{path}"
        headers = kwargs.pop("headers", {})
        headers["Authorization"] = f"Bearer {self.access_token}"
        headers.setdefault("Accept", "application/json")
        try:
            response = self.http.request(method, url, headers=headers, **kwargs)
        except httpx.HTTPError as exc:
            raise ApiError(f"HTTP request failed: {exc}") from exc
        if response.status_code >= 400:
            message = response.text
            try:
                body = response.json()
                message = body.get("error") or body.get("message") or message
            except ValueError:
                pass
            raise ApiError(
                f"{method.upper()} {path} failed with HTTP {response.status_code}: {message}",
                details={"status_code": response.status_code, "path": path},
            )
        if response.status_code == 204 or not response.content:
            return {}
        try:
            return response.json()
        except ValueError as exc:
            raise ApiError(f"{method.upper()} {path} did not return JSON.") from exc

    def list_projects(self) -> list[dict[str, Any]]:
        return self.request("GET", "/open/v1/project")

    def project_data(self, project_id: str) -> dict[str, Any]:
        return self.request("GET", f"/open/v1/project/{project_id}/data")

    def create_task(self, payload: dict[str, Any]) -> dict[str, Any]:
        return self.request("POST", "/open/v1/task", json=payload)

    def complete_task(self, project_id: str, task_id: str) -> dict[str, Any]:
        return self.request("POST", f"/open/v1/project/{project_id}/task/{task_id}/complete")

    def completed_tasks(self, project_id: str | None = None) -> Any:
        if project_id:
            return self.request("GET", f"/open/v1/project/{project_id}/completed")
        return self.request("GET", "/open/v1/project/all/completed")
