# TickTick MCP CLI

简体中文 | [English](README.md)

面向人类和 AI Agent 的 TickTick 国际版 / 滴答清单 Dida365 国内版 CLI 与 MCP 服务器。

TickTick MCP CLI 的目标是让人类用户和 AI Agent 都能安全、清楚、稳定地操作任务系统：

- **人类用户**可以通过易读的命令行管理项目、任务、已完成任务、导出、OAuth 登录和诊断。
- **AI Agent**可以使用稳定 JSON 输出、明确的安全约束、确定性的命令格式，以及基于同一套核心能力的 MCP 工具。

如果你把这个仓库链接发给一个 Agent，它应该只读这份 README 就能理解如何安装、检查认证、列出项目/任务，并使用 MCP 工具。

## 它能做什么

TickTick MCP CLI 使用一个共享 Python Core，并在其上提供两个薄前端：

- **CLI**：`ticktick-mcp-cli`、兼容旧命令 `ticktask` 和短别名 `tt`。
- **MCP Server**：`ticktick-mcp` 和兼容旧命令 `ticktask-mcp`，供支持 Model Context Protocol 的 Agent Runtime 使用。

支持的服务配置：

- `ticktick` → `https://api.ticktick.com`
- `dida365` → `https://api.dida365.com`

当前能力：

- OAuth 凭据初始化和登录。
- 可选系统 keyring 存储 OAuth client secret、access token 和 refresh token。
- 带 OAuth `state` + PKCE 的更安全授权流程。
- 当 `expires_at` 即将过期或已经过期时自动刷新 access token。
- 项目列表、项目数据读取、创建、更新和删除，并校验项目 kind / view mode。
- 任务列表 / 搜索 / 自然语言查询 / 创建 / 获取 / 更新 / 完成 / 删除 / 移动，并支持 due 日期便捷解析（`today`、`tomorrow`、`next monday`、`YYYY-MM-DD`）。
- 面向 Agent 重试的任务创建幂等 key，避免中断/重试时重复创建远端任务。
- 任务提醒设置/清除，以及 repeat/RRULE 重复规则设置/清除。
- 默认 dry-run 的批量完成、删除、移动任务操作。
- 支持标签筛选、智能筛选（today / overdue / upcoming / high-priority / no-date）、priority/status 校验和任务标签增删。
- 支持 `CHECKLIST` 任务的 checklist item / subtask 添加、更新、完成和删除。
- 通过官方 `POST /open/v1/task/completed` API 查询已完成任务。
- 任务分析：统计 open/completed/overdue 数量、项目吞吐、标签分布和优先级分布。
- 进度报告：把任务、习惯打卡和专注时长汇总成一个 scorecard。
- 只读 API 调用支持冲突安全重试，包含 rate limit 的 `Retry-After` 与临时 5xx 处理。
- 面向 Agent 的结构化错误分类：每个错误 payload 都包含 `category`、`retryable` 和 `remediation`。
- 增量 sync/export 状态文件，用于带 checkpoint 的任务导出。
- 按日期/项目写入本地备份文件，支持 Markdown、JSONL、CSV 或 JSON，并生成 manifest。
- 支持官方 habit list/get/create/update、habit check-in/history、focus list/get/delete。
- 将任务、已完成任务或专注会话报表导出为 `json`、`jsonl`、`csv`、`markdown`。
- 生成已脱敏诊断包，便于支持排查和 Agent 交接；配置与 token 密钥只以 `*_configured` 布尔字段呈现。
- 由 `TICKTASK_INTEGRATION=1` 显式开启的只读真实 API smoke 检查。
- 基于同一套 Core 的 MCP 工具和只读 MCP resources。

## 安装

### 方式 A：安装脚本

如果希望一步安装 CLI、MCP server 依赖和系统 keyring 支持，可以运行：

```bash
curl -fsSL https://raw.githubusercontent.com/GeekMai90/ticktick-mcp-cli/main/scripts/install.sh | sh
```

脚本会优先使用 `uv tool install 'ticktick-mcp-cli[mcp,keyring]'`，没有 uv 时回退到 `pipx install 'ticktick-mcp-cli[mcp,keyring]'`，并输出这些验证命令：

```bash
ticktick-mcp-cli --version
ticktick-mcp-cli doctor --json
ticktick-mcp-cli auth status --json
```

### 方式 B：给 Agent 使用的 GitHub npx wrapper

已有 Node.js 的 Agent runtime 可以直接从 GitHub 运行 wrapper，不需要 npm registry 全局包：

```bash
npx github:GeekMai90/ticktick-mcp-cli doctor --json
npx github:GeekMai90/ticktick-mcp-cli auth status --json
npx --package github:GeekMai90/ticktick-mcp-cli ticktick-mcp
```

wrapper 会优先通过 `uvx` 调用 Python 包；没有 `uvx` 时回退到 `python3 -m pipx run`。它本身不保存凭据。

### 方式 C：从 PyPI 安装

```bash
uv tool install ticktick-mcp-cli
# 或
pipx install ticktick-mcp-cli
```

如果希望同时安装 MCP server 依赖，请使用可选的 `mcp` extra：

```bash
uv tool install 'ticktick-mcp-cli[mcp]'
# 或
pipx install 'ticktick-mcp-cli[mcp]'
```

### 方式 D：从 clone 直接使用

```bash
git clone https://github.com/GeekMai90/ticktick-mcp-cli.git
cd ticktick-mcp-cli
uv sync --all-extras --dev
uv run ticktask --help
uv run tt --help
```

### 方式 E：从 GitHub 安装为工具

```bash
uv tool install git+https://github.com/GeekMai90/ticktick-mcp-cli.git
# 或
pipx install git+https://github.com/GeekMai90/ticktick-mcp-cli.git
```

验证：

```bash
ticktick-mcp-cli --version
ticktick-mcp-cli doctor --json
```

命令入口：

- `ticktick-mcp-cli`：主公开 CLI。
- `ticktask`：向后兼容的旧 CLI。
- `tt`：短 CLI 别名。
- `ticktick-mcp`：主公开 stdio MCP Server。
- `ticktask-mcp`：向后兼容的旧 MCP Server。

## 人类用户快速开始

### 1. 初始化 OAuth 应用凭据

先创建 TickTick 或 Dida365 开发者 OAuth App，然后把凭据保存在本机：

```bash
ticktask auth init \
  --service ticktick \
  --client-id "$TICKTICK_CLIENT_ID" \
  --client-secret "$TICKTICK_CLIENT_SECRET" \
  --redirect-uri "http://localhost:8080/callback"
```

如果使用 Dida365：

```bash
ticktask auth init \
  --service dida365 \
  --client-id "$DIDA365_CLIENT_ID" \
  --client-secret "$DIDA365_CLIENT_SECRET" \
  --redirect-uri "http://localhost:8080/callback"
```

查看本地配置路径：

```bash
ticktask config path
```

不要提交本地配置、client secret、access token 或 refresh token。如果希望使用系统级密钥存储，先安装可选 extra（`pipx install 'ticktick-mcp-cli[keyring]'` 或 `uv tool install 'ticktick-mcp-cli[keyring]'`），再用 `--token-storage keyring` 初始化；此时 JSON config 只保留非敏感元数据，client secret、access token 和 refresh token 存入系统 keyring。

### 2. OAuth 登录

启动本地 callback 登录流程：

```bash
ticktask auth login --service ticktick --local-server --json
```

这会打开浏览器，并在已配置的 localhost redirect URI 上等待一次 OAuth callback。

手动浏览器流程：
```bash
ticktask auth login --service ticktick --no-browser --json
```

打开返回的 `authorization_url`。服务商跳转回 callback URL 后，可以用完整 callback URL 完成登录：

```bash
ticktask auth login \
  --service ticktick \
  --callback-url 'http://localhost:8080/callback?code=***&state=STATE' \
  --json
```

也可以使用 code + state：

```bash
ticktask auth login --service ticktick --code CALLBACK_CODE --state STATE --json
```

检查状态：

```bash
ticktask auth status --json
```

### 3. 使用任务能力

```bash
ticktask project list
ticktask task list
ticktask today
ticktask add "Plan release" --project Inbox
ticktask task add "Plan release" --project Inbox --idempotency-key agent-run-123:create-plan-release --json
ticktask task search "release"
ticktask task query "high priority #agent release" --json
ticktask task list --tag agent --filter high-priority
ticktask task filter --tag agent --priority high
ticktask completed today
ticktask task analytics week --project Inbox --json
```

危险变更操作需要精确 ID 和显式确认：

```bash
ticktask project update PROJECT_ID --name "Renamed" --json
ticktask project delete PROJECT_ID --yes --json
ticktask task complete TASK_ID --project-id PROJECT_ID --yes
ticktask task delete TASK_ID --project-id PROJECT_ID --yes
ticktask task move TASK_ID --from-project-id PROJECT_ID --to-project-id OTHER_PROJECT_ID
ticktask task reminder set TASK_ID --project-id PROJECT_ID --reminder TRIGGER:PT10M
ticktask task reminder clear TASK_ID --project-id PROJECT_ID
ticktask task repeat set TASK_ID --project-id PROJECT_ID --preset weekly
ticktask task repeat clear TASK_ID --project-id PROJECT_ID
ticktask task batch complete --task-id TASK_ID_1 --task-id TASK_ID_2 --project-id PROJECT_ID
ticktask task batch delete --task-id TASK_ID --project-id PROJECT_ID --execute --yes
ticktask task batch move --task-id TASK_ID --from-project-id PROJECT_ID --to-project-id OTHER_PROJECT_ID
ticktask task tag add TASK_ID agent --project-id PROJECT_ID
ticktask task tag remove TASK_ID agent --project-id PROJECT_ID
ticktask task item delete TASK_ID ITEM_ID --project-id PROJECT_ID --yes
```

导出示例：

```bash
ticktask export tasks --format jsonl --status all
ticktask export tasks --format csv --project Inbox
ticktask export completed --format markdown --from 2026-05-01 --to 2026-05-17
ticktask export focus --format csv --from 2026-01-01 --to 2026-01-30 --type 0
```

分析和进度报告示例：

```bash
ticktask task analytics today --json
ticktask task analytics week --project Inbox --json
ticktask task analytics --from 2026-05-01 --to 2026-05-17 --json
ticktask report progress week --project Inbox --json
ticktask report progress --from 2026-05-01 --to 2026-05-17 --focus-type 1 --json
```

增量 sync/export 示例：

```bash
ticktask sync state --json
ticktask sync mark tasks:all --timestamp 2026-05-01T00:00:00Z --json
ticktask sync export tasks --format jsonl --state-key tasks:all --status all --save-state --json
```

诊断包示例：

```bash
ticktask doctor bundle --output ./ticktask-diagnostics.zip --json
```

诊断包是一个 ZIP，包含 `diagnostics.json` 和 `report.md`，用于 bug report 和 Agent 交接。它会包含配置路径、当前服务、运行环境、MCP 是否可构建、工具数量等信息，但不会写入 client secret、access token、refresh token、OAuth state 或 PKCE verifier。

备份示例：

```bash
ticktask backup tasks --output-dir ~/ticktask-backups --format markdown,jsonl,csv --status all --json
ticktask backup tasks --output-dir ~/ticktask-backups --date 2026-05-17 --project Inbox --from 2026-05-01 --to 2026-05-17 --json
```

备份文件会写入 `OUTPUT_DIR/YYYY-MM-DD/project-slug/`，并在日期目录生成 `manifest.json`。

## AI Agent 快速开始

### Agent 操作契约

Agent 使用 `ticktask` 时应遵守：

1. 所有支持 `--json` 的 CLI 命令都优先使用 `--json`。
2. 先判断 `ok`，如果 `ok` 为 false，再根据 `error.code` 分支处理。
3. 变更任务前不要凭名称猜测任务或项目 ID；先 list/search，再使用精确 ID。
4. 只有确认目标无误后，才给 `complete` 或 `delete` 传 `--yes`。
5. 将 `TICKTASK_INTEGRATION=1` 视为“允许只读真实 API 调用”的显式授权。
6. 不要打印或提交 OAuth client secret、access token、refresh token、本地 config 或 `.env` 文件。

### 稳定 JSON 协议

成功：

```json
{"ok": true, "data": {}, "meta": {}}
```

失败：

```json
{
  "ok": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Human message",
    "hint": "Next step",
    "category": "validation",
    "retryable": false,
    "remediation": {
      "action": "fix_arguments",
      "command": "rerun with valid arguments",
      "safe_to_retry": false
    }
  }
}
```

结构化错误分类包括 `configuration`、`auth`、`api`、`lookup`、`validation`、`safety`、`unexpected`。Agent 应先判断 `ok`，再根据 `error.code` 分支；只有在 `retryable` 和 `remediation.safe_to_retry` 允许时才重试。

### Agent 安全命令序列

```bash
# 发现当前状态
ticktask doctor --json
ticktask doctor bundle --output ./ticktask-diagnostics.zip --json
ticktask auth status --json
ticktask project list --json
ticktask project create "Focus" --json
ticktask project update PROJECT_ID --name "Renamed" --json
ticktask project delete PROJECT_ID --yes --json

# 读取任务
ticktask task list --json
ticktask task list --status completed --from 2026-05-01 --to 2026-05-17 --json
ticktask task search "release" --json
ticktask task analytics week --json
ticktask report progress week --json
ticktask sync export tasks --format jsonl --state-key tasks:all --status all --json
ticktask backup tasks --output-dir ~/ticktask-backups --format markdown,jsonl --status all --json

# 只有在获得精确 ID 后才做变更
ticktask task add "Plan release" --project Inbox --json
ticktask task add "Plan release" --project Inbox --idempotency-key agent-run-123:create-plan-release --json
ticktask task update TASK_ID --project-id PROJECT_ID --title "New title" --json
ticktask task complete TASK_ID --project-id PROJECT_ID --yes --json
ticktask task delete TASK_ID --project-id PROJECT_ID --yes --json
ticktask task tag add TASK_ID agent --project-id PROJECT_ID --json
ticktask task tag remove TASK_ID agent --project-id PROJECT_ID --json
ticktask task item add TASK_ID "Checklist item" --project-id PROJECT_ID --json
ticktask task item update TASK_ID ITEM_ID --project-id PROJECT_ID --title "Renamed" --status completed --json
ticktask task item complete TASK_ID ITEM_ID --project-id PROJECT_ID --json
ticktask task item delete TASK_ID ITEM_ID --project-id PROJECT_ID --yes --json

# 安全真实 API smoke：默认跳过，显式开启才运行
ticktask integration smoke --json
TICKTASK_INTEGRATION=1 ticktask integration smoke --service dida365 --json
```

## MCP Server

从 clone 开发时安装 MCP 依赖：

```bash
uv sync --extra mcp
uv run ticktick-mcp
```

如果已经作为工具安装：

```bash
ticktask-mcp
```

MCP Server 使用 stdio，并暴露与 CLI 相同 Core 的能力。它也提供只读 MCP resources 和可复用 MCP prompt templates，方便 Agent 获取规划上下文并执行常见工作流。

对于 AI Agent，建议先调用 `ticktask_describe_tools` 查看描述、参数枚举、确认要求和 examples；再用 `ticktask_cli_parity` 映射 MCP tool 与 CLI 命令。需要项目上下文、脱敏本地配置或智能筛选预设时，可读取 `ticktask://projects`、`ticktask://config` 和 `ticktask://saved-views`。日计划、周复盘、安全清理、导出备份等常见场景可直接使用内置 prompt templates。

Agent 创建任务时可给 `ticktask_create_task` 传入 `idempotency_key`。同一个 key 配合同一组创建参数重复调用会返回本地缓存的任务，避免中断重试造成远端重复任务；如果同一个 key 配了不同参数，则会返回校验错误。CLI 对应参数是 `ticktask task add --idempotency-key ...`，幂等记录保存在配置目录旁的 `idempotency.json`。

MCP 工具：

- `ticktask_describe_tools`
- `ticktask_cli_parity`
- `ticktask_doctor`
- `ticktask_diagnostic_bundle`
- `ticktask_auth_status`
- `ticktask_list_projects`
- `ticktask_create_project`
- `ticktask_update_project`
- `ticktask_delete_project`
- `ticktask_list_tasks`
- `ticktask_filter_tasks`
- `ticktask_search_tasks`
- `ticktask_create_task`
- `ticktask_complete_task`
- `ticktask_today`
- `ticktask_get_task`
- `ticktask_update_task`
- `ticktask_delete_task`
- `ticktask_move_task`
- `ticktask_batch_complete_tasks`
- `ticktask_batch_delete_tasks`
- `ticktask_batch_move_tasks`
- `ticktask_set_task_reminders`
- `ticktask_clear_task_reminders`
- `ticktask_set_task_repeat`
- `ticktask_clear_task_repeat`
- `ticktask_add_task_tag`
- `ticktask_remove_task_tag`
- `ticktask_add_checklist_item`
- `ticktask_update_checklist_item`
- `ticktask_complete_checklist_item`
- `ticktask_delete_checklist_item`
- `ticktask_completed`
- `ticktask_task_analytics`
- `ticktask_progress_report`
- `ticktask_list_habits`
- `ticktask_get_habit`
- `ticktask_create_habit`
- `ticktask_update_habit`
- `ticktask_checkin_habit`
- `ticktask_habit_checkins`
- `ticktask_list_focuses`
- `ticktask_get_focus`
- `ticktask_delete_focus`
- `ticktask_export_tasks`
- `ticktask_sync_state`
- `ticktask_mark_sync_state`
- `ticktask_sync_export_tasks`
- `ticktask_backup_tasks`
- `ticktask_export_focuses`

MCP resources：

- `ticktask://projects`：只读项目列表，用于规划和精确 ID 查询。
- `ticktask://config`：已脱敏的当前服务 / profile 配置，不暴露 secrets。
- `ticktask://saved-views`：内置智能筛选预设，以及对应 MCP/CLI 参数。

MCP prompts：

- `ticktask_daily_planning`：基于项目上下文和 saved views 做今日计划。
- `ticktask_weekly_review`：结合任务分析、已完成任务、习惯和专注记录做周复盘。
- `ticktask_cleanup`：先 dry-run 批量操作，安全识别待清理任务。
- `ticktask_export`：导出、备份或增量同步任务数据。

## 真实 API integration smoke

默认是安全跳过：

```bash
ticktask integration smoke --json
```

除非显式开启，否则返回 `skipped: true`。

执行只读真实 API 检查：

```bash
TICKTASK_INTEGRATION=1 ticktask integration smoke --service dida365 --json
```

它只会列出项目并返回 `project_count`，不会创建、更新、完成、移动或删除项目或任务。

## 开发

```bash
git clone https://github.com/GeekMai90/ticktick-mcp-cli.git
cd ticktick-mcp-cli
uv sync --all-extras --dev
uv run pytest -q
uv run ticktick-mcp-cli --help
uv run ticktick-mcp-cli doctor --json
uv run --with 'mcp>=1.0' python -c 'from ticktask.mcp.server import build_server; build_server(); print("mcp_build_ok")'
uv build
```

## 文档

- [Docs Index](docs/index.md)
- [Agent-First Quickstart](docs/agent-quickstart.md)
- [Installation](docs/installation.md)
- [OAuth](docs/oauth.md)
- [CLI Usage](docs/cli-usage.md)
- [MCP Usage](docs/mcp-usage.md)
- [MCP Integration Examples for Claude Desktop, Hermes, Cursor, Claude Code, and OpenClaw](docs/integrations.md)
- [Agent Usage](docs/agent-usage.md)
- [Release Checklist](docs/release.md)
- [Roadmap: competitive parity and best-in-class agent workflows](docs/roadmap.md)
- [Original Implementation Plan](docs/plans/2026-05-17-ticktask-cli-mcp-plan.md)

## 安全说明

- 本地配置默认保存在仓库外。
- `.env`、token 文件、本地 config、`dist/` 和 build 输出都被 git 忽略。
- OAuth 登录使用 state 和 PKCE。
- API 调用会在 access token 过期或即将过期时自动 refresh。
- 只读 API 调用会重试临时限流/服务器错误；写入类操作不会盲目重试，避免重复创建或重复修改。
- 创建任务可使用本地幂等 key；同一 key + 同一 payload 会复用结果，同一 key + 不同 payload 会拒绝。
- 全局查询已完成任务时会故意省略 `projectIds`，避免漏掉 Dida365 已完成任务。

## License

MIT. See [LICENSE](LICENSE).



