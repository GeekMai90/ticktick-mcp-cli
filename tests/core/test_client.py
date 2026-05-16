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


def test_completed_tasks_can_call_global_endpoint() -> None:
    urls = []

    def handler(request: httpx.Request) -> httpx.Response:
        urls.append(str(request.url))
        return httpx.Response(200, json=[])

    client = TicktaskClient(
        "https://api.dida365.com",
        "token",
        http_client=httpx.Client(transport=httpx.MockTransport(handler)),
    )

    assert client.completed_tasks() == []
    assert urls == ["https://api.dida365.com/open/v1/project/all/completed"]
