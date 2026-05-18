#!/usr/bin/env sh
set -eu

PACKAGE="${TICKTASK_INSTALL_PACKAGE:-ticktick-mcp-cli}"
EXTRAS="${TICKTASK_INSTALL_EXTRAS:-mcp,keyring}"
DRY_RUN="${TICKTASK_INSTALL_DRY_RUN:-0}"

with_extras() {
  if [ -n "$EXTRAS" ]; then
    printf "%s[%s]" "$PACKAGE" "$EXTRAS"
  else
    printf "%s" "$PACKAGE"
  fi
}

install_target="$(with_extras)"

printf "TickTick MCP CLI installer\n"
printf "Package: %s\n" "$install_target"

if command -v uv >/dev/null 2>&1; then
  printf "Using uv tool install.\n"
  if [ "$DRY_RUN" = "1" ]; then
    printf "+ uv tool install '%s'\n" "$install_target"
  else
    uv tool install "$install_target"
  fi
elif command -v pipx >/dev/null 2>&1; then
  printf "Using pipx install.\n"
  if [ "$DRY_RUN" = "1" ]; then
    printf "+ pipx install '%s'\n" "$install_target"
  else
    pipx install "$install_target"
  fi
else
  printf "Install uv or pipx, then re-run this installer.\n" >&2
  printf "Suggested: curl -LsSf https://astral.sh/uv/install.sh | sh\n" >&2
  exit 1
fi

printf "\nVerify the installation:\n"
printf "  ticktick-mcp-cli --version\n"
printf "  ticktick-mcp-cli doctor --json\n"
printf "  ticktick-mcp-cli auth status --json\n"
printf "\nFor Dida365, initialize auth with --service dida365.\n"
