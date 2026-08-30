<div align="center">

# MemPalace Codex 插件

简体中文 | [English](README.en.md)

</div>

[MemPalace](https://github.com/MemPalace/mempalace) 面向 Codex 的独立适配插件。MemPalace 负责存储、检索、checkpoint 和知识图谱；本项目只提供 Codex 的 MCP 注册、会话归档和使用规则。

目前已在 MemPalace `v3.8.0` 上完成测试。它用于替代官方 Codex 插件；同一 Codex profile 中只能启用其中之一。

## 适配范围

- 注册官方 `mempalace-mcp`，不修改其 MCP 工具或 MemPalace CLI 行为。
- 由插件自身提供 `SessionStart`、`Stop`、`PreCompact` 三个 Hook。
- 针对当前 Codex JSONL，归档逐字的用户消息和最终助手回复；跳过系统消息、工具协议与已确认的 Codex 注入内容（`<recommended_plugins>`、`<skill>`）。
- 正常 `Stop` 按用户回合数归档，默认 15；`PreCompact` 无条件启动一次归档。
- 保留官方五个 skills：`help`、`init`、`mine`、`search`、`status`，并增加 `mempalace-codex`，说明项目级检索、显式 checkpoint 与原始会话归档的边界。

## 与官方插件的差异

| 项目 | 本插件的行为 |
| --- | --- |
| MCP 与通用 skills | 复用 MemPalace 的 MCP 接口和通用 skills；当前在 `v3.8.0` 上测试。 |
| Hook 注册 | 使用插件的 `hooks/hooks.json`；不使用用户级 Hook。 |
| 生命周期 | 只处理 `SessionStart`、`Stop`、`PreCompact`；不处理 `SessionEnd`。 |
| transcript 解析 | 适配当前 Codex JSONL，仅保存用户文本和最终助手文本，并过滤两种已确认的 Codex 注入标记。 |
| Stop 周期 | 默认每 15 个用户回合，可由插件配置或环境变量覆盖。 |

## 安装

### 1. 先部署并配置 MemPalace

按照 [MemPalace 的安装与配置文档](https://mempalaceofficial.com/guide/configuration.html) 完成后端、palace 路径和 embedding 配置，再确认下面命令可以运行：

```bash
mempalace status
```

安装 MemPalace CLI：

```bash
uv tool install mempalace
```

### 2. 安装 Hook runner

它必须位于 Codex 的 `PATH`，以便插件 Hook 能启动：

```bash
uv tool install "git+https://github.com/ScreamWolf/mempalace-codex-plugin.git@main"
```

安装完成后确认两个命令都可解析：

```bash
command -v mempalace-mcp
command -v mempalace-codex-hook
command -v mempalace-codex-mcp
```

若系统没有将 uv 的工具目录加入 `PATH`，先修正该环境配置后再安装插件。

### 3. 在 Codex 安装插件

将本仓库作为 marketplace 添加，然后安装插件：

```bash
codex plugin marketplace add ScreamWolf/mempalace-codex-plugin
codex plugin add mempalace-codex-plugin@mempalace-codex-plugin
```

也可在 Codex Desktop 的插件目录中选择该 marketplace 安装。首次启用时，Codex 会要求审阅并信任插件提供的 Hook；这是预期的安全边界。安装或升级后，请新开一个任务，使 MCP 和 skills 从新插件副本加载。

## 升级

Codex 插件副本与 `uv tool` 中的 Hook runner 是两个独立安装项。只重新安装
Codex 插件不会刷新 runner；升级时应依次更新两者：

```bash
uv tool install --force --refresh "git+https://github.com/ScreamWolf/mempalace-codex-plugin.git@main"
codex plugin add mempalace-codex-plugin@mempalace-codex-plugin
```

完成后新开一个任务验证 `SessionStart`，并让后续 MCP、skills 与 Hook 都从新版本启动。

## 配置

可选配置位于 `~/.config/mempalace-codex/config.toml`：

```toml
[archive]
# Stop 后累计多少个用户回合才归档；默认值为 15。
interval_user_turns = 15

[mcp]
# 仅在 MemPalace 使用 Qdrant 或 pgvector 等服务端协调并发写入的后端时开启。
# 本地 Chroma 等后端仍会由官方 MCP 强制保持单 writer。
allow_peer_writer = false
```

可用环境变量临时覆盖归档间隔：

```bash
MEMPALACE_CODEX_ARCHIVE_INTERVAL=5
```

多个 Codex 项目共用同一个 Qdrant / pgvector palace 时，将 `[mcp]` 的
`allow_peer_writer` 设为 `true`。插件启动官方 `mempalace-mcp` 前才会注入
对应的官方环境变量；默认值为 `false`，保持官方单 writer 行为。

## 许可

MIT
