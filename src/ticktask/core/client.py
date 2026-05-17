from __future__ import annotations

from collections.abc import Callable, Sequence
from datetime import date, datetime
from email.utils import parsedate_to_datetime
from time import sleep
from typing import Any

import httpx

from ticktask.core.errors import ApiError


def request_json_without_auth(
    base_url: str,
    method: str,
    path: str,
    http_client: httpx.Client | None = None,
    **kwargs: Any,
) -> Any:
    client = http_client or httpx.Client(timeout=20)
    owns_client = http_client is None
    try:
        response = client.request(method, f"{base_url.rstrip('/')}{path}", **kwargs)
    except httpx.HTTPError as exc:
        raise ApiError(f"HTTP request failed: {exc}") from exc
    finally:
        if owns_client:
            client.close()
    return _decode_response(response, method, path)


class TicktaskClient:
    def __init__(
        self,
        base_url: str,
        access_token: str,
        http_client: httpx.Client | None = None,
        max_retries: int = 2,
        retry_sleep: Callable[[float], None] = sleep,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.access_token = access_token
        self.max_retries = max(0, max_retries)
        self._retry_sleep = retry_sleep
        self._owns_client = http_client is None
        self.http = http_client or httpx.Client(timeout=20)

    def close(self) -> None:
        if self._owns_client:
            self.http.close()

    def __enter__(self) -> TicktaskClient:
        return self

    def __exit__(self, *_exc: object) -> None:
        self.close()

    def request(self, method: str, path: str, retry: bool | None = None, **kwargs: Any) -> Any:
        url = f"{self.base_url}{path}"
        headers = kwargs.pop("headers", {})
        headers["Authorization"] = f"Bearer {self.access_token}"
        headers.setdefault("Accept", "application/json")
        retryable = _is_retryable_request(method, retry)
        last_exc: httpx.HTTPError | None = None
        for attempt in range(self.max_retries + 1):
            try:
                response = self.http.request(method, url, headers=headers, **kwargs)
            except httpx.HTTPError as exc:
                last_exc = exc
                if retryable and attempt < self.max_retries:
                    self._retry_sleep(_backoff_delay(attempt))
                    continue
                raise ApiError(
                    f"HTTP request failed: {exc}",
                    details={"path": path, "retryable": retryable},
                ) from exc

            if _should_retry_response(response, retryable) and attempt < self.max_retries:
                self._retry_sleep(_retry_delay(response, attempt))
                continue
            return _decode_response(response, method, path, retryable=retryable)

        if last_exc is not None:  # defensive; the loop normally raises above.
            raise ApiError(
                f"HTTP request failed: {last_exc}",
                details={"path": path, "retryable": retryable},
            ) from last_exc
        raise ApiError("HTTP request failed after retries.", details={"path": path, "retryable": retryable})

    def list_projects(self) -> list[dict[str, Any]]:
        return self.request("GET", "/open/v1/project")

    def project_data(self, project_id: str) -> dict[str, Any]:
        return self.request("GET", f"/open/v1/project/{project_id}/data")

    def create_project(self, payload: dict[str, Any]) -> dict[str, Any]:
        return self.request("POST", "/open/v1/project", json=payload)

    def update_project(self, project_id: str, payload: dict[str, Any]) -> dict[str, Any]:
        return self.request("POST", f"/open/v1/project/{project_id}", json=payload)

    def delete_project(self, project_id: str) -> dict[str, Any]:
        return self.request("DELETE", f"/open/v1/project/{project_id}")

    def create_task(self, payload: dict[str, Any]) -> dict[str, Any]:
        return self.request("POST", "/open/v1/task", json=payload)

    def complete_task(self, project_id: str, task_id: str) -> dict[str, Any]:
        return self.request("POST", f"/open/v1/project/{project_id}/task/{task_id}/complete")

    def get_task(self, project_id: str, task_id: str) -> dict[str, Any]:
        return self.request("GET", f"/open/v1/project/{project_id}/task/{task_id}")

    def update_task(self, task_id: str, payload: dict[str, Any]) -> dict[str, Any]:
        return self.request("POST", f"/open/v1/task/{task_id}", json=payload)

    def delete_task(self, project_id: str, task_id: str) -> dict[str, Any]:
        return self.request("DELETE", f"/open/v1/project/{project_id}/task/{task_id}")

    def move_task(self, task_id: str, from_project_id: str, to_project_id: str) -> dict[str, Any]:
        payload = [
            {
                "fromProjectId": from_project_id,
                "toProjectId": to_project_id,
                "taskId": task_id,
            }
        ]
        return self.request("POST", "/open/v1/task/move", json=payload)

    def filter_tasks(self, payload: dict[str, Any]) -> Any:
        return self.request("POST", "/open/v1/task/filter", json=payload, retry=True)

    def completed_tasks(
        self,
        start_date: str | date | datetime | None = None,
        end_date: str | date | datetime | None = None,
        project_ids: str | Sequence[str] | None = None,
    ) -> Any:
        payload: dict[str, Any] = {
            "startDate": self._format_date(start_date or "1970-01-01"),
            "endDate": self._format_date(end_date or date.today()),
        }
        normalized_project_ids = self._normalize_project_ids(project_ids)
        if normalized_project_ids:
            payload["projectIds"] = normalized_project_ids
        return self.request("POST", "/open/v1/task/completed", json=payload, retry=True)


    def list_habits(self) -> Any:
        return self.request("GET", "/open/v1/habit")

    def get_habit(self, habit_id: str) -> dict[str, Any]:
        return self.request("GET", f"/open/v1/habit/{habit_id}")

    def create_habit(self, payload: dict[str, Any]) -> dict[str, Any]:
        return self.request("POST", "/open/v1/habit", json=payload)

    def update_habit(self, habit_id: str, payload: dict[str, Any]) -> dict[str, Any]:
        return self.request("POST", f"/open/v1/habit/{habit_id}", json=payload)

    def checkin_habit(self, habit_id: str, payload: dict[str, Any]) -> dict[str, Any]:
        return self.request("POST", f"/open/v1/habit/{habit_id}/checkin", json=payload)

    def habit_checkins(self, habit_ids: str | Sequence[str], from_stamp: int, to_stamp: int) -> Any:
        normalized_habit_ids = self._normalize_project_ids(habit_ids)
        params = {"habitIds": ",".join(normalized_habit_ids), "from": from_stamp, "to": to_stamp}
        return self.request("GET", "/open/v1/habit/checkins", params=params)

    def get_focus(self, focus_id: str, focus_type: int = 0) -> dict[str, Any]:
        return self.request("GET", f"/open/v1/focus/{focus_id}", params={"type": focus_type})

    def list_focuses(self, from_time: str, to_time: str, focus_type: int = 0) -> Any:
        return self.request("GET", "/open/v1/focus", params={"from": from_time, "to": to_time, "type": focus_type})

    def delete_focus(self, focus_id: str, focus_type: int = 0) -> dict[str, Any]:
        return self.request("DELETE", f"/open/v1/focus/{focus_id}", params={"type": focus_type})

    @staticmethod
    def _format_date(value: str | date | datetime) -> str:
        if isinstance(value, datetime):
            return value.isoformat()
        if isinstance(value, date):
            return value.isoformat()
        return value

    @staticmethod
    def _normalize_project_ids(project_ids: str | Sequence[str] | None) -> list[str]:
        if project_ids is None:
            return []
        if isinstance(project_ids, str):
            return [project_ids] if project_ids else []
        return [project_id for project_id in project_ids if project_id]


def _is_retryable_request(method: str, retry: bool | None) -> bool:
    if retry is not None:
        return retry
    return method.upper() in {"GET", "HEAD", "OPTIONS"}


def _should_retry_response(response: httpx.Response, retryable: bool) -> bool:
    return retryable and (response.status_code == 429 or 500 <= response.status_code <= 599)


def _retry_delay(response: httpx.Response, attempt: int) -> float:
    retry_after = _parse_retry_after(response.headers.get("Retry-After"))
    if retry_after is not None:
        return retry_after
    return _backoff_delay(attempt)


def _backoff_delay(attempt: int) -> float:
    return min(2.0**attempt, 30.0)


def _parse_retry_after(value: str | None) -> float | None:
    if not value:
        return None
    try:
        return max(0.0, float(value))
    except ValueError:
        try:
            retry_at = parsedate_to_datetime(value)
        except (TypeError, ValueError):
            return None
        if retry_at.tzinfo is None:
            retry_at = retry_at.astimezone()
        return max(0.0, (retry_at - datetime.now(retry_at.tzinfo)).total_seconds())


def _decode_response(response: httpx.Response, method: str, path: str, retryable: bool = False) -> Any:
    if response.status_code >= 400:
        message = response.text
        try:
            body = response.json()
            if isinstance(body, dict):
                message = body.get("error") or body.get("message") or message
        except ValueError:
            pass
        details: dict[str, Any] = {"status_code": response.status_code, "path": path}
        retry_after = _parse_retry_after(response.headers.get("Retry-After"))
        if retry_after is not None:
            details["retry_after"] = retry_after
        details["retryable"] = retryable
        raise ApiError(
            f"{method.upper()} {path} failed with HTTP {response.status_code}: {message}",
            details=details,
        )
    if response.status_code == 204 or not response.content:
        return {}
    try:
        return response.json()
    except ValueError as exc:
        raise ApiError(f"{method.upper()} {path} did not return JSON.") from exc
