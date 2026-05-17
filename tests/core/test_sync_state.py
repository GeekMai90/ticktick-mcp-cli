import json

from ticktask.core.sync_state import SyncStateStore


def test_sync_state_store_round_trips_keys_and_timestamps(tmp_path) -> None:
    store = SyncStateStore(tmp_path / "sync-state.json")

    empty = store.load()
    assert empty == {"version": 1, "states": {}}

    marked = store.mark("tasks:all", "2026-05-17T00:00:00Z")

    assert marked["state_key"] == "tasks:all"
    assert marked["last_synced_at"] == "2026-05-17T00:00:00Z"
    assert marked["state_path"].endswith("sync-state.json")
    assert json.loads((tmp_path / "sync-state.json").read_text())["states"]["tasks:all"]["last_synced_at"] == "2026-05-17T00:00:00Z"
    assert store.get("tasks:all")["last_synced_at"] == "2026-05-17T00:00:00Z"


def test_sync_state_store_validates_state_key_and_timestamp(tmp_path) -> None:
    store = SyncStateStore(tmp_path / "sync-state.json")

    for key in ["", "   "]:
        try:
            store.mark(key, "2026-05-17T00:00:00Z")
        except ValueError as exc:
            assert "state key" in str(exc)
        else:
            raise AssertionError("expected ValueError")

    try:
        store.mark("tasks", "not-a-timestamp")
    except ValueError as exc:
        assert "timestamp" in str(exc)
    else:
        raise AssertionError("expected ValueError")
