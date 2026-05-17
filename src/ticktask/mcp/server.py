from __future__ import annotations

import sys

from ticktask.mcp import resources, tools


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
    server.tool()(tools.ticktask_describe_tools)
    for tool_name in tools.TOOL_DEFINITIONS:
        server.tool()(getattr(tools, tool_name))
    for uri, definition in resources.RESOURCE_DEFINITIONS.items():
        server.resource(
            uri,
            name=definition["name"],
            title=definition["title"],
            description=definition["description"],
            mime_type=definition["mime_type"],
        )(definition["function"])
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
