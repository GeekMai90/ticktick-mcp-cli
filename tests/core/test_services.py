from ticktask.core.auth import AuthManager
from ticktask.core.config import ConfigStore
from ticktask.core.errors import ConfirmationRequiredError
from ticktask.core.errors import ValidationError
from ticktask.core.services import TicktaskService


class FakeClient:
    def __init__(self):
        self.closed = False
        self.completed_calls = []
        self.updated_payloads = []

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

    def get_task(self, project_id, task_id):
        return {
            "id": task_id,
            "title": "Loaded",
            "projectId": project_id,
            "kind": "CHECKLIST",
            "items": [
                {"id": "i1", "title": "Existing", "status": 0, "sortOrder": 1},
                {"id": "i2", "title": "Done", "status": 1, "sortOrder": 2},
            ],
        }

    def update_task(self, task_id, payload):
        self.updated_payloads.append(payload)
        return {"id": task_id, **payload}

    def delete_task(self, project_id, task_id):
        return {"deleted": True, "projectId": project_id, "taskId": task_id}

    def move_task(self, task_id, from_project_id, to_project_id):
        return {"moved": True, "taskId": task_id, "from": from_project_id, "to": to_project_id}

    def create_project(self, payload):
        return {"id": "new-project", **payload}

    def update_project(self, project_id, payload):
        return {"id": project_id, **payload}

    def delete_project(self, project_id):
        return {"deleted": True, "projectId": project_id}

    def completed_tasks(self, start_date=None, end_date=None, project_ids=None):
        self.completed_calls.append(
            {"start_date": start_date, "end_date": end_date, "project_ids": project_ids}
        )
        project_id = project_ids[0] if project_ids else "p1"
        return [{"id": "t2", "title": "Done item", "status": 2, "projectId": project_id}]

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


def test_list_completed_uses_global_completed_query_without_project_ids(tmp_path) -> None:
    fake = FakeClient()
    manager = AuthManager(ConfigStore(tmp_path / "config.json"))
    manager.init("dida365", "client", "secret", "http://localhost", access_token="token")
    svc = TicktaskService(auth=manager, client_factory=lambda _profile: fake)

    tasks = svc.list_tasks(status="completed")

    assert tasks[0]["id"] == "t2"
    assert len(fake.completed_calls) == 1
    assert fake.completed_calls[0]["start_date"] == "1970-01-01"
    assert fake.completed_calls[0]["end_date"] is not None
    assert fake.completed_calls[0]["project_ids"] is None


def test_list_completed_with_project_passes_project_ids_and_dates(tmp_path) -> None:
    fake = FakeClient()
    manager = AuthManager(ConfigStore(tmp_path / "config.json"))
    manager.init("ticktick", "client", "secret", "http://localhost", access_token="token")
    svc = TicktaskService(auth=manager, client_factory=lambda _profile: fake)

    tasks = svc.list_tasks(
        project="Inbox",
        status="completed",
        start_date="2026-01-01",
        end_date="2026-01-31",
    )

    assert tasks[0]["id"] == "t2"
    assert fake.completed_calls == [
        {"start_date": "2026-01-01", "end_date": "2026-01-31", "project_ids": ["p1"]}
    ]


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


def test_task_crud_move_and_export(tmp_path) -> None:
    svc = service(tmp_path)
    assert svc.get_task("t1", "p1")["title"] == "Loaded"
    updated = svc.update_task("t1", "p1", title="Renamed", priority="medium")
    assert updated["title"] == "Renamed"
    assert updated["priority"] == 3
    deleted = svc.delete_task("t1", "p1", confirmed=True)
    assert deleted["result"]["deleted"] is True
    moved = svc.move_task("t1", "p1", "p2")
    assert moved["to_project_id"] == "p2"
    assert "Buy milk" in svc.export_tasks("markdown")


def test_update_requires_changed_field(tmp_path) -> None:
    try:
        service(tmp_path).update_task("t1", "p1")
    except ValidationError as exc:
        assert exc.code == "VALIDATION_ERROR"
    else:
        raise AssertionError("expected ValidationError")


def test_project_lifecycle_service_methods(tmp_path) -> None:
    svc = service(tmp_path)

    created = svc.create_project("Focus", color="#00aa00", view_mode="list", kind="TASK")
    assert created["id"] == "new-project"
    assert created["name"] == "Focus"
    assert created["raw"]["color"] == "#00aa00"

    updated = svc.update_project("p1", name="Renamed", color="#111111", closed=True)
    assert updated["id"] == "p1"
    assert updated["name"] == "Renamed"
    assert updated["raw"]["closed"] is True

    deleted = svc.delete_project("p1", confirmed=True)
    assert deleted == {"project_id": "p1", "result": {"deleted": True, "projectId": "p1"}}


def test_project_delete_requires_confirmation(tmp_path) -> None:
    try:
        service(tmp_path).delete_project("p1", confirmed=False)
    except ConfirmationRequiredError as exc:
        assert exc.code == "CONFIRMATION_REQUIRED"
    else:
        raise AssertionError("expected ConfirmationRequiredError")


def test_update_project_requires_changed_field(tmp_path) -> None:
    try:
        service(tmp_path).update_project("p1")
    except ValidationError as exc:
        assert exc.code == "VALIDATION_ERROR"
    else:
        raise AssertionError("expected ValidationError")


def test_checklist_item_crud_updates_task_items(tmp_path) -> None:
    fake = FakeClient()
    manager = AuthManager(ConfigStore(tmp_path / "config.json"))
    manager.init("ticktick", "client", "secret", "http://localhost", access_token="token")
    svc = TicktaskService(auth=manager, client_factory=lambda _profile: fake)

    added = svc.add_checklist_item("t1", "p1", "New item", item_id="i-new")
    assert added["kind"] == "CHECKLIST"
    assert added["items"][-1]["id"] == "i-new"
    assert fake.updated_payloads[-1]["items"][-1]["status"] == 0

    updated = svc.update_checklist_item("t1", "p1", "i1", title="Renamed", status=1)
    assert updated["items"][0]["title"] == "Renamed"
    assert updated["items"][0]["status"] == 1

    completed = svc.complete_checklist_item("t1", "p1", "i1")
    assert completed["items"][0]["status"] == 1

    deleted = svc.delete_checklist_item("t1", "p1", "i2", confirmed=True)
    assert [item["id"] for item in deleted["items"]] == ["i1"]


def test_checklist_item_delete_requires_confirmation(tmp_path) -> None:
    try:
        service(tmp_path).delete_checklist_item("t1", "p1", "i1", confirmed=False)
    except ConfirmationRequiredError as exc:
        assert exc.code == "CONFIRMATION_REQUIRED"
    else:
        raise AssertionError("expected ConfirmationRequiredError")


def test_checklist_item_update_requires_existing_item_and_change(tmp_path) -> None:
    svc = service(tmp_path)
    try:
        svc.update_checklist_item("t1", "p1", "missing", title="Nope")
    except ValidationError as exc:
        assert exc.code == "VALIDATION_ERROR"
    else:
        raise AssertionError("expected ValidationError")

    try:
        svc.update_checklist_item("t1", "p1", "i1")
    except ValidationError as exc:
        assert exc.code == "VALIDATION_ERROR"
    else:
        raise AssertionError("expected ValidationError")
