#!/usr/bin/env node
"use strict";

const { spawnSync } = require("node:child_process");
const path = require("node:path");

const SPEC = process.env.TICKTASK_NPX_SPEC || "ticktick-mcp-cli[mcp,keyring] @ git+https://github.com/GeekMai90/ticktick-mcp-cli.git";
const DRY_RUN = process.env.TICKTASK_NPX_DRY_RUN === "1";

function commandExists(command) {
  const probe = process.platform === "win32" ? "where" : "command";
  const args = process.platform === "win32" ? [command] : ["-v", command];
  const result = spawnSync(probe, args, { stdio: "ignore", shell: process.platform !== "win32" });
  return result.status === 0;
}

function targetCommand() {
  const invoked = path.basename(process.argv[1] || "ticktick-mcp-cli");
  return invoked.includes("ticktick-mcp") && !invoked.includes("ticktick-mcp-cli")
    ? "ticktick-mcp"
    : "ticktick-mcp-cli";
}

function printCommand(command, args) {
  console.log([command, ...args].join(" "));
}

function run(command, args) {
  if (DRY_RUN) {
    printCommand(command, args);
    return 0;
  }
  const result = spawnSync(command, args, { stdio: "inherit" });
  if (result.error) {
    console.error(result.error.message);
    return 1;
  }
  return result.status ?? 1;
}

const target = targetCommand();
const forwardedArgs = process.argv.slice(2);

if (commandExists("uvx")) {
  process.exit(run("uvx", ["--from", SPEC, target, ...forwardedArgs]));
}

if (commandExists("python3")) {
  process.exit(run("python3", ["-m", "pipx", "run", "--spec", SPEC, target, ...forwardedArgs]));
}

console.error("Install uv/uvx or Python with pipx, then run this npx wrapper again.");
process.exit(1);
