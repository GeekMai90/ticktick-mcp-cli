from __future__ import annotations

import sys

from ticktask.mcp import tools


INSTALL_HINT = (
    "ticktask MCP server requires the optional `mcp` package. "
    "Install with `uv pip install 'ticktick-mcp-cli[mcp]'` or `pip install 'ticktick-mcp-cli[mcp]'`."
)


def build_server():
    try:
        from mcp.server.fastmcp import FastMCP
    except Exception as exc:
        raise RuntimeError(INSTALL_HINT) from exc

    server = FastMCP("ticktask")
    server.tool()(tools.ticktask_doctor)
    server.tool()(tools.ticktask_auth_status)
    server.tool()(tools.ticktask_list_projects)
    server.tool()(tools.ticktask_create_project)
    server.tool()(tools.ticktask_update_project)
    server.tool()(tools.ticktask_delete_project)
    server.tool()(tools.ticktask_list_tasks)
    server.tool()(tools.ticktask_search_tasks)
    server.tool()(tools.ticktask_create_task)
    server.tool()(tools.ticktask_complete_task)
    server.tool()(tools.ticktask_today)
    server.tool()(tools.ticktask_get_task)
    server.tool()(tools.ticktask_update_task)
    server.tool()(tools.ticktask_delete_task)
    server.tool()(tools.ticktask_move_task)
    server.tool()(tools.ticktask_add_checklist_item)
    server.tool()(tools.ticktask_update_checklist_item)
    server.tool()(tools.ticktask_complete_checklist_item)
    server.tool()(tools.ticktask_delete_checklist_item)
    server.tool()(tools.ticktask_completed)
    server.tool()(tools.ticktask_export_tasks)
    return server


def main() -> None:
    try:
        server = build_server()
    except RuntimeError as exc:
        print(str(exc), file=sys.stderr)
        raise SystemExit(2) from exc
    server.run()


if __name__ == "__main__":
    main()
