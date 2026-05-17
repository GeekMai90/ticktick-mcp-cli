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
- 带 OAuth `state` + PKCE 的更安全授权流程。
- 当 `expires_at` 即将过期或已经过期时自动刷新 access token。
- 项目列表、项目数据读取、创建、更新和删除。
- 任务列表 / 搜索 / 创建 / 获取 / 更新 / 完成 / 删除 / 移动。
- 任务提醒设置/清除，以及 repeat/RRULE 重复规则设置/清除。
- 默认 dry-run 的批量完成、删除、移动任务操作。
- 支持标签筛选、智能筛选（today / overdue / upcoming / high-priority / no-date）和任务标签增删。
- 支持 `CHECKLIST` 任务的 checklist item / subtask 添加、更新、完成和删除。
- 通过官方 `POST /open/v1/task/completed` API 查询已完成任务。
- 任务分析：统计 open/completed/overdue 数量、项目吞吐、标签分布和优先级分布。
- 进度报告：把任务、习惯打卡和专注时长汇总成一个 scorecard。
- 只读 API 调用支持冲突安全重试，包含 rate limit 的 `Retry-After` 与临时 5xx 处理。
- 增量 sync/export 状态文件，用于带 checkpoint 的任务导出。
- 按日期/项目写入本地备份文件，支持 Markdown、JSONL、CSV 或 JSON，并生成 manifest。
- 支持官方 habit list/get/create/update、habit check-in/history、focus list/get/delete。
- 将任务、已完成任务或专注会话报表导出为 `json`、`jsonl`、`csv`、`markdown`。
- 由 `TICKTASK_INTEGRATION=1` 显式开启的只读真实 API smoke 检查。
- 基于同一套 Core 的 MCP 工具。

## 安装

### 方式 A：从 clone 直接使用

```bash
git clone https://github.com/GeekMai90/ticktick-mcp-cli.git
cd ticktick-mcp-cli
uv sync --all-extras --dev
uv run ticktask --help
uv run tt --help
```

### 方式 B：从 GitHub 安装为工具

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

不要提交本地配置、client secret、access token 或 refresh token。

### 2. OAuth 登录

启动浏览器 / 手动登录流程：

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
ticktask task search "release"
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
{"ok": false, "error": {"code": "ERROR_CODE", "message": "Human message", "hint": "Next step"}}
```

### Agent 安全命令序列

```bash
# 发现当前状态
ticktask doctor --json
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

MCP Server 使用 stdio，并暴露与 CLI 相同 Core 的能力。

对于 AI Agent，建议先调用 `ticktask_describe_tools` 查看描述、参数枚举、确认要求和 examples；再用 `ticktask_cli_parity` 映射 MCP tool 与 CLI 命令。

MCP 工具：

- `ticktask_describe_tools`
- `ticktask_cli_parity`
- `ticktask_doctor`
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
- `ticktask_export_focuses`

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

- [Installation](docs/installation.md)
- [OAuth](docs/oauth.md)
- [CLI Usage](docs/cli-usage.md)
- [MCP Usage](docs/mcp-usage.md)
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
- 全局查询已完成任务时会故意省略 `projectIds`，避免漏掉 Dida365 已完成任务。

## License

MIT. See [LICENSE](LICENSE).



