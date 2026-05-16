import httpx

from ticktask.core.client import TicktaskClient


def test_client_adds_bearer_token_and_base_url() -> None:
    seen = {}

    def handler(request: httpx.Request) -> httpx.Response:
        seen["url"] = str(request.url)
        seen["auth"] = request.headers["Authorization"]
        return httpx.Response(200, json=[{"id": "p1", "name": "Inbox"}])

    client = TicktaskClient(
        "https://api.ticktick.com",
        "token",
        http_client=httpx.Client(transport=httpx.MockTransport(handler)),
    )

    assert client.list_projects() == [{"id": "p1", "name": "Inbox"}]
    assert seen == {
        "url": "https://api.ticktick.com/open/v1/project",
        "auth": "Bearer token",
    }


def test_completed_tasks_posts_global_body_without_project_ids() -> None:
    seen = {}

    def handler(request: httpx.Request) -> httpx.Response:
        seen["method"] = request.method
        seen["url"] = str(request.url)
        seen["body"] = request.read()
        return httpx.Response(200, json=[])

    client = TicktaskClient(
        "https://api.dida365.com",
        "token",
        http_client=httpx.Client(transport=httpx.MockTransport(handler)),
    )

    assert client.completed_tasks(start_date="2026-01-01", end_date="2026-01-31") == []
    assert seen["method"] == "POST"
    assert seen["url"] == "https://api.dida365.com/open/v1/task/completed"
    assert seen["body"] == b'{"startDate":"2026-01-01","endDate":"2026-01-31"}'


def test_completed_tasks_posts_project_ids_when_supplied() -> None:
    seen = {}

    def handler(request: httpx.Request) -> httpx.Response:
        seen["method"] = request.method
        seen["url"] = str(request.url)
        seen["body"] = request.read()
        return httpx.Response(200, json=[])

    client = TicktaskClient(
        "https://api.ticktick.com",
        "token",
        http_client=httpx.Client(transport=httpx.MockTransport(handler)),
    )

    assert (
        client.completed_tasks(
            start_date="2026-01-01",
            end_date="2026-01-31",
            project_ids=["p1", "p2"],
        )
        == []
    )
    assert seen["method"] == "POST"
    assert seen["url"] == "https://api.ticktick.com/open/v1/task/completed"
    assert seen["body"] == (
        b'{"startDate":"2026-01-01","endDate":"2026-01-31",'
        b'"projectIds":["p1","p2"]}'
    )
