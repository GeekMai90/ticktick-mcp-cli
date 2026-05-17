from __future__ import annotations

from typing import Any


def ticktask_daily_planning(
    project: str | None = None,
    include_overdue: bool = True,
) -> str:
    """Prompt template for planning a safe daily task list."""
    scope = project or "all projects"
    overdue_step = (
        "- Include the `overdue` saved view when sequencing the day.\n"
        if include_overdue
        else "- Do not include overdue-only analysis unless it is directly relevant.\n"
    )
    return f"""Plan today's TickTick/Dida365 work for {scope}.

Context to read first:
- Read `ticktask://projects` to resolve project names to exact IDs.
- Read `ticktask://saved-views` to understand the built-in planning views.

Safe workflow:
- Call `ticktask_list_tasks` for `today`, and for `overdue` when requested.
{overdue_step}- Use `ticktask_create_task` only for explicit new tasks the user asks to add.
- Use `ticktask_update_task` only after exact task/project ID verification.
- Treat batch changes as dry-run first; say "dry-run" in your plan before any mutation.

Output:
- Summarize must-do, should-do, and optional tasks.
- Mention which tool calls you used and which IDs you verified.
"""


def ticktask_weekly_review(
    project: str | None = None,
    period: str = "week",
) -> str:
    """Prompt template for weekly review and progress reporting."""
    scope = project or "all projects"
    return f"""Review TickTick/Dida365 progress for {scope} over `{period}`.

Context to read first:
- Read `ticktask://projects` for project context and exact IDs.
- Use `ticktask_progress_report` for the cross-domain scorecard.
- Use `ticktask_task_analytics` for open/completed/overdue counts, throughput, tags, and priorities.
- Use `ticktask_completed` to inspect completed task details.

Rules:
- Do not mutate tasks during review unless the user explicitly asks.
- For Dida365 global completed-task queries, do not pass project IDs unless the user scopes to a project.

Output:
- Wins, blockers, overdue risks, next-week suggestions, and any follow-up tasks to confirm with the user.
"""


def ticktask_cleanup(
    project: str | None = None,
    older_than_days: int = 30,
) -> str:
    """Prompt template for safe task cleanup."""
    scope = project or "all projects"
    return f"""Clean up TickTick/Dida365 tasks for {scope}, focusing on stale items older than {older_than_days} days.

Context to read first:
- Read `ticktask://projects` to resolve exact project IDs.
- Read `ticktask://saved-views` for `overdue` and `no-date` cleanup candidates.
- Call `ticktask_list_tasks` to inspect candidates before proposing changes.

Safety workflow:
- Never delete or complete immediately.
- Use `ticktask_batch_complete_tasks` or `ticktask_batch_delete_tasks` with `dry_run=true` first.
- Only execute with `dry_run=false` and `yes=true` after the user approves the exact task IDs.

Output:
- Candidate groups, rationale, dry-run command/tool arguments, and a clear approval checkpoint.
"""


def ticktask_export(
    project: str | None = None,
    output_format: str = "markdown",
    output_dir: str = "~/ticktask-backups",
) -> str:
    """Prompt template for exports, backups, and incremental sync handoffs."""
    scope = project or "all projects"
    return f"""Export TickTick/Dida365 task data for {scope} as `{output_format}`.

Context to read first:
- Read `ticktask://projects` to resolve exact scope.
- Call `ticktask_sync_state` to inspect existing incremental checkpoints.

Export options:
- Use `ticktask_export_tasks` for immediate content returned to the caller.
- Use `ticktask_backup_tasks` to write files under `{output_dir}`.
- Use `ticktask_sync_export_tasks` for checkpointed incremental exports.

Rules:
- Prefer read-only/export operations; do not mutate remote tasks.
- Explain where files are written and what format was produced.
"""


PROMPT_DEFINITIONS: dict[str, dict[str, Any]] = {
    "ticktask_daily_planning": {
        "function": ticktask_daily_planning,
        "title": "Daily planning",
        "description": "Plan today's work using projects, saved views, and safe task operations.",
    },
    "ticktask_weekly_review": {
        "function": ticktask_weekly_review,
        "title": "Weekly review",
        "description": "Review weekly task, habit, and focus progress without mutating tasks.",
    },
    "ticktask_cleanup": {
        "function": ticktask_cleanup,
        "title": "Safe cleanup",
        "description": "Find stale task cleanup candidates with dry-run batch operations first.",
    },
    "ticktask_export": {
        "function": ticktask_export,
        "title": "Export and backup",
        "description": "Export, back up, or incrementally sync task data without remote mutations.",
    },
}
