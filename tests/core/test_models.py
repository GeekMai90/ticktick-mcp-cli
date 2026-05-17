

def test_task_model_exposes_checklist_items_and_kind() -> None:
    from ticktask.core.models import Task

    task = Task.from_api(
        {
            "id": "t1",
            "projectId": "p1",
            "title": "Checklist",
            "kind": "CHECKLIST",
            "items": [{"id": "i1", "title": "First", "status": 0}],
        }
    ).to_dict()

    assert task["kind"] == "CHECKLIST"
    assert task["items"] == [{"id": "i1", "title": "First", "status": 0}]
