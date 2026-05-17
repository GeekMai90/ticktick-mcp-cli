import json

from ticktask.core.exporters import serialize_tasks


TASKS = [
    {
        "id": "t1",
        "project_id": "p1",
        "title": "Alpha",
        "content": "Body",
        "due_date": "2026-01-01",
        "priority": 3,
        "status": 0,
        "raw": {"ignored": True},
    }
]


def test_serialize_tasks_json() -> None:
    payload = json.loads(serialize_tasks(TASKS, "json"))
    assert payload == [
        {
            "content": "Body",
            "due_date": "2026-01-01",
            "id": "t1",
            "priority": 3,
            "project_id": "p1",
            "status": 0,
            "title": "Alpha",
        }
    ]


def test_serialize_tasks_jsonl_csv_markdown() -> None:
    assert serialize_tasks(TASKS, "jsonl").startswith('{"content": "Body"')
    assert serialize_tasks(TASKS, "csv").splitlines()[0] == (
        "id,project_id,title,content,due_date,priority,status"
    )
    assert "| t1 | p1 | Alpha | 2026-01-01 | 3 | 0 |" in serialize_tasks(TASKS, "markdown")
