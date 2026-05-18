#!/usr/bin/env sh
set -eu

PACKAGE_SPEC="${TICKTASK_INSTALL_SPEC:-ticktick-mcp-cli[mcp,keyring] @ git+https://github.com/GeekMai90/ticktick-mcp-cli.git}"
DRY_RUN="${TICKTASK_INSTALL_DRY_RUN:-0}"

printf "TickTick MCP CLI installer
"
printf "Package spec: %s
" "$PACKAGE_SPEC"

if command -v uv >/dev/null 2>&1; then
  printf "Using uv tool install.
"
  if [ "$DRY_RUN" = "1" ]; then
    printf "+ uv tool install '%s'
" "$PACKAGE_SPEC"
  else
    uv tool install "$PACKAGE_SPEC"
  fi
elif command -v pipx >/dev/null 2>&1; then
  printf "Using pipx install.
"
  if [ "$DRY_RUN" = "1" ]; then
    printf "+ pipx install '%s'
" "$PACKAGE_SPEC"
  else
    pipx install "$PACKAGE_SPEC"
  fi
else
  printf "Install uv or pipx, then re-run this installer.
" >&2
  printf "Suggested: curl -LsSf https://astral.sh/uv/install.sh | sh
" >&2
  exit 1
fi

printf "
Verify the installation:
"
printf "  ticktick-mcp-cli --version
"
printf "  ticktick-mcp-cli doctor --json
"
printf "  ticktick-mcp-cli auth status --json
"
printf "
For Dida365, initialize auth with --service dida365.
"
