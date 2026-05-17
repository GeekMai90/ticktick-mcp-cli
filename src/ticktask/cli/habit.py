from __future__ import annotations

import typer

from ticktask.cli.formatters import emit_error, emit_json
from ticktask.core.results import ok
from ticktask.core.services import TicktaskService

app = typer.Typer(help="Habit commands.")


@app.command("list")
def list_habits(json_output: bool = typer.Option(False, "--json", help="Emit stable JSON.")) -> None:
    try:
        habits = TicktaskService().list_habits()
        if json_output:
            emit_json(ok(habits, {"count": len(habits)}))
        else:
            for habit in habits:
                typer.echo(f"{habit['id']}\t{habit['name']}")
    except Exception as exc:
        emit_error(exc, json_output)


@app.command("get")
def get_habit(habit_id: str, json_output: bool = typer.Option(False, "--json", help="Emit stable JSON.")) -> None:
    try:
        habit = TicktaskService().get_habit(habit_id)
        if json_output:
            emit_json(ok(habit))
        else:
            typer.echo(f"{habit['id']}\t{habit['name']}")
    except Exception as exc:
        emit_error(exc, json_output)


@app.command("create")
def create_habit(
    name: str,
    goal: int | None = typer.Option(None, "--goal", help="Goal value."),
    step: int | None = typer.Option(None, "--step", help="Step increment."),
    unit: str | None = typer.Option(None, "--unit", help="Unit label."),
    repeat_rule: str | None = typer.Option(None, "--repeat-rule", help="iCal RRULE."),
    json_output: bool = typer.Option(False, "--json", help="Emit stable JSON."),
) -> None:
    try:
        habit = TicktaskService().create_habit(name, goal=goal, step=step, unit=unit, repeat_rule=repeat_rule)
        if json_output:
            emit_json(ok(habit))
        else:
            typer.echo(f"{habit['id']}\t{habit['name']}")
    except Exception as exc:
        emit_error(exc, json_output)


@app.command("update")
def update_habit(
    habit_id: str,
    name: str | None = typer.Option(None, "--name", help="New habit name."),
    goal: int | None = typer.Option(None, "--goal", help="Goal value."),
    step: int | None = typer.Option(None, "--step", help="Step increment."),
    unit: str | None = typer.Option(None, "--unit", help="Unit label."),
    repeat_rule: str | None = typer.Option(None, "--repeat-rule", help="iCal RRULE."),
    json_output: bool = typer.Option(False, "--json", help="Emit stable JSON."),
) -> None:
    try:
        habit = TicktaskService().update_habit(
            habit_id,
            name=name,
            goal=goal,
            step=step,
            unit=unit,
            repeat_rule=repeat_rule,
        )
        if json_output:
            emit_json(ok(habit))
        else:
            typer.echo(f"{habit['id']}\t{habit['name']}")
    except Exception as exc:
        emit_error(exc, json_output)


@app.command("checkin")
def checkin_habit(
    habit_id: str,
    stamp: int,
    value: int = typer.Option(1, "--value", help="Check-in value."),
    json_output: bool = typer.Option(False, "--json", help="Emit stable JSON."),
) -> None:
    try:
        result = TicktaskService().checkin_habit(habit_id, stamp=stamp, value=value)
        if json_output:
            emit_json(ok(result))
        else:
            typer.echo(f"Checked in habit {habit_id} for {stamp}.")
    except Exception as exc:
        emit_error(exc, json_output)


@app.command("history")
def habit_history(
    habit_ids: list[str] = typer.Argument(..., help="One or more habit IDs."),
    from_stamp: int = typer.Option(..., "--from", help="Start stamp as YYYYMMDD."),
    to_stamp: int = typer.Option(..., "--to", help="End stamp as YYYYMMDD."),
    json_output: bool = typer.Option(False, "--json", help="Emit stable JSON."),
) -> None:
    try:
        history = TicktaskService().habit_checkins(habit_ids, from_stamp=from_stamp, to_stamp=to_stamp)
        if json_output:
            emit_json(ok(history, {"count": len(history)}))
        else:
            for item in history:
                typer.echo(str(item))
    except Exception as exc:
        emit_error(exc, json_output)
