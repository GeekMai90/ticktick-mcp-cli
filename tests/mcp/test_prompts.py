from ticktask.mcp import prompts
from ticktask.mcp.server import build_server


def test_prompt_templates_are_registered_and_agent_friendly() -> None:
    assert set(prompts.PROMPT_DEFINITIONS) == {
        "ticktask_daily_planning",
        "ticktask_weekly_review",
        "ticktask_cleanup",
        "ticktask_export",
    }

    for name, definition in prompts.PROMPT_DEFINITIONS.items():
        assert definition["function"] is getattr(prompts, name)
        assert definition["title"]
        assert definition["description"]


def test_daily_planning_prompt_references_safe_context_and_tools() -> None:
    text = prompts.ticktask_daily_planning(project="Inbox", include_overdue=True)

    assert "ticktask://projects" in text
    assert "ticktask://saved-views" in text
    assert "ticktask_list_tasks" in text
    assert "ticktask_create_task" in text
    assert "ticktask_update_task" in text
    assert "dry-run" in text.lower()
    assert "Inbox" in text
    assert "overdue" in text


def test_weekly_review_prompt_uses_reports_and_completed_queries() -> None:
    text = prompts.ticktask_weekly_review(project="Deep Work", period="week")

    assert "ticktask_progress_report" in text
    assert "ticktask_task_analytics" in text
    assert "ticktask_completed" in text
    assert "ticktask://projects" in text
    assert "Deep Work" in text
    assert "week" in text


def test_cleanup_prompt_keeps_mutations_confirmed_and_preview_first() -> None:
    text = prompts.ticktask_cleanup(project="Inbox", older_than_days=30)

    assert "ticktask://saved-views" in text
    assert "ticktask_list_tasks" in text
    assert "ticktask_batch_complete_tasks" in text
    assert "ticktask_batch_delete_tasks" in text
    assert "dry_run=true" in text
    assert "yes=true" in text
    assert "30" in text


def test_export_prompt_includes_backup_and_incremental_paths() -> None:
    text = prompts.ticktask_export(project="Inbox", output_format="markdown", output_dir="~/ticktask-backups")

    assert "ticktask_export_tasks" in text
    assert "ticktask_backup_tasks" in text
    assert "ticktask_sync_export_tasks" in text
    assert "ticktask_sync_state" in text
    assert "markdown" in text
    assert "~/ticktask-backups" in text


def test_build_server_registers_prompt_templates() -> None:
    server = build_server()
    prompt_names = {prompt.name for prompt in server._prompt_manager.list_prompts()}

    assert {
        "ticktask_daily_planning",
        "ticktask_weekly_review",
        "ticktask_cleanup",
        "ticktask_export",
    } <= prompt_names
