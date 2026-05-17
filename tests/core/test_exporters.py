import json

from ticktask.core.exporters import serialize_focuses, serialize_tasks


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

FOCUSES = [
    {
        "id": "f1",
        "focus_type": 0,
        "task_id": "t1",
        "start_time": "2026-01-01T09:00:00+0000",
        "end_time": "2026-01-01T09:25:00+0000",
        "duration": 1500,
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


def test_serialize_focuses_includes_report_friendly_fields() -> None:
    payload = json.loads(serialize_focuses(FOCUSES, "json"))
    assert payload == [
        {
            "id": "f1",
            "focus_type": 0,
            "task_id": "t1",
            "start_time": "2026-01-01T09:00:00+0000",
            "end_time": "2026-01-01T09:25:00+0000",
            "duration_seconds": 1500,
            "duration_minutes": 25,
        }
    ]
    assert serialize_focuses(FOCUSES, "csv").splitlines()[0] == (
        "id,focus_type,task_id,start_time,end_time,duration_seconds,duration_minutes"
    )
    assert "| f1 | 0 | t1 | 2026-01-01T09:00:00+0000 | 2026-01-01T09:25:00+0000 | 1500 | 25 |" in serialize_focuses(FOCUSES, "markdown")
