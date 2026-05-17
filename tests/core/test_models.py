

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



def test_habit_and_focus_models_expose_stable_fields() -> None:
    from ticktask.core.models import Focus, Habit

    habit = Habit.from_api({"id": "h1", "name": "Read", "status": 0, "totalCheckIns": 3}).to_dict()
    assert habit["id"] == "h1"
    assert habit["name"] == "Read"
    assert habit["total_checkins"] == 3

    focus = Focus.from_api({"id": "f1", "type": 0, "taskId": "t1", "duration": 1500}).to_dict()
    assert focus["id"] == "f1"
    assert focus["focus_type"] == 0
    assert focus["task_id"] == "t1"
    assert focus["duration"] == 1500
