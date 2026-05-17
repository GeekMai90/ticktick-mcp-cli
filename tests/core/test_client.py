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


def test_task_crud_and_move_endpoints() -> None:
    calls = []

    def handler(request: httpx.Request) -> httpx.Response:
        calls.append((request.method, str(request.url), request.read()))
        return httpx.Response(200, json={"id": "t1", "title": "Task", "projectId": "p1"})

    client = TicktaskClient(
        "https://api.ticktick.com",
        "token",
        http_client=httpx.Client(transport=httpx.MockTransport(handler)),
    )

    client.get_task("p1", "t1")
    client.update_task("t1", {"id": "t1", "projectId": "p1", "title": "Renamed"})
    client.delete_task("p1", "t1")
    client.move_task("t1", "p1", "p2")

    assert calls[0] == (
        "GET",
        "https://api.ticktick.com/open/v1/project/p1/task/t1",
        b"",
    )
    assert calls[1][0:2] == ("POST", "https://api.ticktick.com/open/v1/task/t1")
    assert calls[2] == (
        "DELETE",
        "https://api.ticktick.com/open/v1/project/p1/task/t1",
        b"",
    )
    assert calls[3] == (
        "POST",
        "https://api.ticktick.com/open/v1/task/move",
        b'[{"fromProjectId":"p1","toProjectId":"p2","taskId":"t1"}]',
    )


def test_project_lifecycle_endpoints() -> None:
    calls = []

    def handler(request: httpx.Request) -> httpx.Response:
        calls.append((request.method, str(request.url), request.read()))
        if request.method == "DELETE":
            return httpx.Response(204)
        return httpx.Response(200, json={"id": "p1", "name": "Renamed", "color": "#ff0000"})

    client = TicktaskClient(
        "https://api.ticktick.com",
        "token",
        http_client=httpx.Client(transport=httpx.MockTransport(handler)),
    )

    assert client.create_project({"name": "Inbox", "color": "#ff0000"})["id"] == "p1"
    assert client.update_project("p1", {"id": "p1", "name": "Renamed"})["name"] == "Renamed"
    assert client.delete_project("p1") == {}

    assert calls == [
        (
            "POST",
            "https://api.ticktick.com/open/v1/project",
            b'{"name":"Inbox","color":"#ff0000"}',
        ),
        (
            "POST",
            "https://api.ticktick.com/open/v1/project/p1",
            b'{"id":"p1","name":"Renamed"}',
        ),
        ("DELETE", "https://api.ticktick.com/open/v1/project/p1", b""),
    ]



def test_habit_endpoints() -> None:
    calls = []

    def handler(request: httpx.Request) -> httpx.Response:
        calls.append((request.method, str(request.url), request.read()))
        if request.method == "DELETE":
            return httpx.Response(204)
        if str(request.url).endswith("/checkins?habitIds=h1,h2&from=20260101&to=20260131"):
            return httpx.Response(200, json=[{"habitId": "h1", "checkins": []}])
        return httpx.Response(200, json={"id": "h1", "name": "Read"})

    client = TicktaskClient(
        "https://api.ticktick.com",
        "token",
        http_client=httpx.Client(transport=httpx.MockTransport(handler)),
    )

    client.list_habits()
    client.get_habit("h1")
    client.create_habit({"name": "Read"})
    client.update_habit("h1", {"id": "h1", "name": "Read more"})
    client.checkin_habit("h1", {"stamp": 20260101, "value": 1})
    client.habit_checkins(["h1", "h2"], 20260101, 20260131)

    assert calls == [
        ("GET", "https://api.ticktick.com/open/v1/habit", b""),
        ("GET", "https://api.ticktick.com/open/v1/habit/h1", b""),
        ("POST", "https://api.ticktick.com/open/v1/habit", b'{"name":"Read"}'),
        ("POST", "https://api.ticktick.com/open/v1/habit/h1", b'{"id":"h1","name":"Read more"}'),
        ("POST", "https://api.ticktick.com/open/v1/habit/h1/checkin", b'{"stamp":20260101,"value":1}'),
        ("GET", "https://api.ticktick.com/open/v1/habit/checkins?habitIds=h1%2Ch2&from=20260101&to=20260131", b""),
    ]


def test_focus_endpoints() -> None:
    calls = []

    def handler(request: httpx.Request) -> httpx.Response:
        calls.append((request.method, str(request.url), request.read()))
        if request.method == "DELETE":
            return httpx.Response(204)
        return httpx.Response(200, json={"id": "f1", "type": 0})

    client = TicktaskClient(
        "https://api.ticktick.com",
        "token",
        http_client=httpx.Client(transport=httpx.MockTransport(handler)),
    )

    client.get_focus("f1", focus_type=0)
    client.list_focuses(from_time="2026-01-01T00:00:00+0000", to_time="2026-01-02T00:00:00+0000", focus_type=1)
    client.delete_focus("f1", focus_type=0)

    assert calls == [
        ("GET", "https://api.ticktick.com/open/v1/focus/f1?type=0", b""),
        ("GET", "https://api.ticktick.com/open/v1/focus?from=2026-01-01T00%3A00%3A00%2B0000&to=2026-01-02T00%3A00%3A00%2B0000&type=1", b""),
        ("DELETE", "https://api.ticktick.com/open/v1/focus/f1?type=0", b""),
    ]
