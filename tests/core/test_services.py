from ticktask.core.auth import AuthManager
from ticktask.core.config import ConfigStore
from ticktask.core.errors import ConfirmationRequiredError
from ticktask.core.services import TicktaskService


class FakeClient:
    def __init__(self):
        self.closed = False
        self.completed_project_ids = []

    def list_projects(self):
        return [{"id": "p1", "name": "Inbox"}]

    def project_data(self, project_id):
        return {
            "tasks": [
                {"id": "t1", "title": "Buy milk", "status": 0, "projectId": project_id},
                {"id": "t2", "title": "Done item", "status": 2, "projectId": project_id},
            ]
        }

    def create_task(self, payload):
        return {"id": "new", **payload}

    def complete_task(self, project_id, task_id):
        return {"completed": True, "projectId": project_id, "taskId": task_id}

    def completed_tasks(self, project_id=None):
        self.completed_project_ids.append(project_id)
        return [{"id": "t2", "title": "Done item", "status": 2, "projectId": project_id or "p1"}]

    def close(self):
        self.closed = True


def service(tmp_path) -> TicktaskService:
    manager = AuthManager(ConfigStore(tmp_path / "config.json"))
    manager.init("ticktick", "client", "secret", "http://localhost", access_token="token")
    return TicktaskService(auth=manager, client_factory=lambda _profile: FakeClient())


def test_list_tasks_filters_open(tmp_path) -> None:
    tasks = service(tmp_path).list_tasks(status="open")
    assert [task["id"] for task in tasks] == ["t1"]


def test_search_tasks(tmp_path) -> None:
    tasks = service(tmp_path).search_tasks("milk")
    assert len(tasks) == 1
    assert tasks[0]["id"] == "t1"


def test_list_completed_uses_global_completed_endpoint(tmp_path) -> None:
    fake = FakeClient()
    manager = AuthManager(ConfigStore(tmp_path / "config.json"))
    manager.init("dida365", "client", "secret", "http://localhost", access_token="token")
    svc = TicktaskService(auth=manager, client_factory=lambda _profile: fake)

    tasks = svc.list_tasks(status="completed")

    assert tasks[0]["id"] == "t2"
    assert fake.completed_project_ids == [None]


def test_create_task_resolves_project(tmp_path) -> None:
    task = service(tmp_path).create_task("New task", project="Inbox", priority="high")
    assert task["id"] == "new"
    assert task["project_id"] == "p1"
    assert task["priority"] == 5


def test_complete_requires_confirmation(tmp_path) -> None:
    try:
        service(tmp_path).complete_task("t1", "p1", confirmed=False)
    except ConfirmationRequiredError as exc:
        assert exc.code == "CONFIRMATION_REQUIRED"
    else:
        raise AssertionError("expected ConfirmationRequiredError")
