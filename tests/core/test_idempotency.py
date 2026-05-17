from ticktask.core.idempotency import IdempotencyStore
from ticktask.core.errors import ValidationError


def test_idempotency_store_replays_matching_fingerprint(tmp_path) -> None:
    store = IdempotencyStore(tmp_path / "idempotency.json")
    result = {"id": "t1", "title": "Write"}

    assert store.get("task.create", "key-1", {"title": "Write"}) is None
    store.record("task.create", "key-1", {"title": "Write"}, result)

    replayed = store.get("task.create", "key-1", {"title": "Write"})
    assert replayed == result


def test_idempotency_store_rejects_same_key_with_different_fingerprint(tmp_path) -> None:
    store = IdempotencyStore(tmp_path / "idempotency.json")
    store.record("task.create", "key-1", {"title": "Write"}, {"id": "t1"})

    try:
        store.get("task.create", "key-1", {"title": "Different"})
    except ValidationError as exc:
        assert exc.code == "VALIDATION_ERROR"
        assert "different payload" in exc.message
    else:
        raise AssertionError("expected ValidationError")
