# OpenSpec Schema 通用化设计

## Context

当前 `openspec/config.yaml` 混合了通用配置和项目特定配置（语言偏好、mermaid 语法、数据库/模块假设等），导致 schema 无法直接复用于其他项目。`AGENTS.md` 已承载项目信息，但 OpenSpec 项目特定规则分散在 `config.yaml` 中。

## Goals / Non-Goals

### Goals
- `openspec/schemas/superpowers-bridge/schema.yaml` 保持完全通用（已达成，无需改动）
- `openspec/config.yaml` 只保留真正通用的 OpenSpec 配置
- 项目特定规则迁移到 `AGENTS.md`，由 OpenCode LLM 读取执行
- 不破坏现有 `opsx:*` 工作流

### Non-Goals
- 不改动 schema 模板文件（已是通用占位符模式）
- 不改动 `.opencode/commands/*`（工作流不变）
- 不改动现有 activity change（qwen-chatbot-api-key-settings）

## Decisions

### Decision 1: 区分通用 vs 项目特定规则

| 规则 | 归属 | 理由 |
|------|------|------|
| 必须包含回滚方案 | config.yaml | 任何生产系统变更都应有回滚方案 |
| 每个 Requirement 包含正常/异常 Scenario | config.yaml | 测试驱动的最佳实践，项目无关 |
| 简体中文要求 | AGENTS.md | 语言偏好，不是 schema 的职责 |
| mermaid 语法 | AGENTS.md | 文档格式偏好，非 schema 通用约束 |
| workflows profile | AGENTS.md | OpenSpec profile 选型，项目决策 |
| 标注模块/数据库/API 影响 | AGENTS.md | 假设项目有特定架构（模块、数据库、API） |

### Decision 2: AGENTS.md 作为项目特定规则的唯一来源

`AGENTS.md` 已被 `opencode.json` 注册为 `instructions`，LLM 在每次会话中自动加载。将项目特定规则放在 AGENTS.md 中，LLM 在执行 `opsx:*` 命令生成 artifact 时自动遵从这些约束。

### Decision 3: 不修改 schema 模板

`openspec/schemas/superpowers-bridge/templates/*` 已是通用的占位符模式，无需改动。

## Risks / Trade-offs

- **Risk**: 脱离 OpenCode 直接使用 `openspec` CLI 时，AGENTS.md 规则不会自动注入
- **Mitigation**: 本项目所有开发通过 OpenCode `opsx:*` 命令进行，不直接调用 `openspec` CLI
- **Trade-off**: `config.yaml` 的 `rules` 会被 `openspec instructions` 输出显式列出给 LLM；AGENTS.md 规则则作为系统级别指令，覆盖所有 artifact

## Migration Plan

1. 更新 `openspec/config.yaml`：移除项目特定项
2. 更新 `AGENTS.md`：在 `## OpenSpec + Superpowers 工作流` 下新增 `### OpenSpec 项目配置规则` 小节
3. 验证：确认 `openspec status` 和 artifact 生成正常

## Testing Strategy

- 运行 `openspec validate` 确保配置有效
- 确认 AGENTS.md 仍被 `opencode.json` 引用
