# TickTick MCP CLI 简体中文手册

这是一份面向中文用户和 AI Agent 的简体中文入口。项目定位是 **Agent-first**：人类用户不需要记 CLI 命令，可以直接用自然语言告诉 Agent 要做什么；CLI 和 MCP Server 负责提供稳定、安全、可验证的执行层。

> 国内用户优先使用 `dida365` 服务配置，也就是滴答清单国内版：`https://api.dida365.com`。

## 1. 适合谁阅读

- **使用 Hermes / Claude Desktop / Cursor / Claude Code / OpenClaw 的用户**：把仓库链接发给 Agent，让它按本文安装、配置、检查。
- **实现 Agent 集成的开发者**：重点看 MCP Server、工具安全边界、只读 smoke test、写操作确认策略。
- **需要排查问题的人**：使用 `doctor`、`auth status` 和诊断包定位本地配置、OAuth、keyring、MCP runtime 问题。

如果只是日常使用，推荐直接对 Agent 说：

```text
帮我在滴答清单里加个任务：明天上午处理发票报销。
```

Agent 应该负责选择 MCP 工具、校验结果，并给出简洁反馈。

## 2. 一键安装

推荐安装脚本：

```bash
curl -fsSL https://raw.githubusercontent.com/GeekMai90/ticktick-mcp-cli/main/scripts/install.sh | sh
```

安装后检查：

```bash
ticktick-mcp-cli --version
ticktick-mcp-cli doctor --json
ticktick-mcp-cli auth status --json
```

安装成功后可用命令入口：

- `ticktick-mcp-cli`：主 CLI。
- `ticktask`：兼容旧名称的 CLI。
- `tt`：短别名。
- `ticktick-mcp`：主 stdio MCP Server。
- `ticktask-mcp`：兼容旧名称的 MCP Server。

## 3. 配置 Dida365 OAuth

先在 Dida365 / TickTick 开发者后台创建 OAuth App，并确保 redirect URI 与本地配置完全一致。国内滴答清单示例：

```bash
ticktask auth init \
  --service dida365 \
  --client-id "$DIDA365_CLIENT_ID" \
  --client-secret "$DIDA365_CLIENT_SECRET" \
  --redirect-uri "http://localhost:8080/callback" \
  --token-storage keyring \
  --json
```

然后登录：

```bash
ticktask auth login --service dida365 --local-server --json
```

检查登录状态：

```bash
ticktask auth status --service dida365 --json
```

安全约定：

- 不要把 `client_secret`、`access_token`、`refresh_token` 粘贴到公开 issue、PR、日志或聊天里。
- 如果使用 `--token-storage keyring`，JSON config 只保存非敏感元数据，密钥进入系统 keyring。
- Agent 做诊断时只能汇报 `*_configured` 这类布尔状态，不应输出真实 secret/token。

## 4. 接入 MCP Runtime

### Hermes

```bash
hermes mcp add ticktask --command ticktask-mcp
hermes mcp test ticktask
```

如果是在 Telegram / Discord Gateway 中使用，添加 MCP server 后需要重启 Gateway 才会在新会话加载。重启会短暂断开消息平台，Agent 应先征得用户同意。

### Claude Desktop / Cursor / 其他 Runtime

通用 stdio 配置形态：

```json
{
  "mcpServers": {
    "ticktask": {
      "command": "ticktask-mcp"
    }
  }
}
```

如果 runtime 找不到命令，使用绝对路径：

```bash
which ticktask-mcp
```

然后把返回路径写入 `command`。

## 5. 只读 smoke test

Agent 接入后，先做只读测试，不要立刻创建、完成或删除任务。

建议提示词：

```text
List my projects. Do not create, update, complete, or delete tasks.
```

对应 CLI 检查：

```bash
ticktask project list --json
```

如果失败，先看：

```bash
ticktask doctor --json
ticktask auth status --service dida365 --json
```

## 6. Agent 应该怎么使用

### 创建任务

用户自然语言：

```text
帮我加个任务：明天上午处理发票报销。
```

Agent 应该调用创建任务能力，必要时选择项目、解析日期，并在成功后回复：

```text
已创建：明天上午处理发票报销
清单：默认清单或用户指定清单
日期：明天上午
```

创建任务通常可以直接执行；为避免网络重试造成重复创建，Agent 应使用幂等 key。

### 查询任务

用户自然语言：

```text
查一下今天滴答清单里有什么任务。
```

Agent 应使用 today/list/search/filter 等只读能力，并用简洁中文总结，不要把完整 JSON 直接贴给用户。

### 完成 / 删除 / 批量操作

这些属于有副作用的操作，Agent 必须更保守：

1. 先查出候选任务；
2. 展示标题、清单、任务 ID 或可识别信息；
3. 等用户确认；
4. 再执行完成、删除、移动等操作。

批量完成 / 批量删除 / 批量移动应先 dry-run，再等用户确认后执行。

## 7. MCP 能力概览

当前 MCP Server 暴露能力包括：

- 项目：列出、创建、更新、删除。
- 任务：列出、搜索、自然语言 query、创建、获取、更新、完成、删除、移动。
- 批量任务：批量完成、删除、移动，默认 dry-run。
- Checklist：添加、更新、完成、删除 checklist item / subtask。
- 标签：添加、移除、按标签筛选。
- 提醒与重复：设置/清除 reminders，设置/清除 repeat/RRULE。
- 已完成任务：支持 Dida365 全局 completed 查询；未显式限定项目时不要传 `projectIds`。
- 习惯与专注：habit list/get/create/update/check-in/history，focus list/get/delete/export。
- 导出与备份：任务、专注会话、增量 sync、备份 manifest。
- 报告：任务分析、进度报告。
- 诊断：doctor、auth status、脱敏诊断包、CLI/MCP parity。
- MCP resources：项目上下文、脱敏配置、saved views。
- MCP prompts：每日规划、周回顾、安全清理、导出备份。

## 8. 常见问题

### 为什么默认要强调 Dida365？

TickTick 国际版和国内滴答清单使用不同 API base URL。中文用户通常使用 Dida365，如果误用 `ticktick` 配置，可能出现 401、空列表或查不到任务。

### 为什么 Agent 不应该直接删除任务？

删除、完成、批量移动都是不可忽略的副作用。为了避免误操作，Agent 应先展示候选和 dry-run 结果，等用户确认后再执行。

### 为什么输出 JSON？

CLI 的 JSON 输出主要给 Agent 和自动化流程使用。最终给人的回复应该由 Agent 总结成简洁中文。

## 9. 更多文档

- [英文文档首页](index.md)
- [Agent 快速开始](agent-quickstart.md)
- [安装说明](installation.md)
- [OAuth 说明](oauth.md)
- [MCP 使用说明](mcp-usage.md)
- [Agent 使用规则](agent-usage.md)
- [Runtime 集成](integrations.md)
- [路线图](roadmap.md)
