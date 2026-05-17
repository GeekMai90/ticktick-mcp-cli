

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


def test_task_model_exposes_tags() -> None:
    from ticktask.core.models import Task

    task = Task.from_api(
        {
            "id": "t1",
            "projectId": "p1",
            "title": "Tagged",
            "tags": ["agent", "deep-work"],
        }
    ).to_dict()

    assert task["tags"] == ["agent", "deep-work"]
