## 摘要

<!--
一段话概览（硬限制：50-300 字符）：
現狀（1 句）→ 變更（1 句）→ 用戶價值（1 句）

這是最常被讀的段落——利益相關者、審批人、新加入的團隊成員。
寫不清楚的話後面沒人會看完。
-->

## Why

<!--
动机（硬限制：50-1000 字符，OpenSpec zod schema 會 validate）。
建議結構：現況痛點 → 為什麼現在處理 → 預期收益（各 1-2 句）

注意：不要重複摘要的內容，這裡提供更多上下文和數據。
-->

## 用户价值

<!--
这个变更给用户带来什么可感知的改善？

建议结构：
- 目标用户（谁受益）
- 使用场景（在什么情况下）
- 可感知变化（原来怎样 → 现在怎样）
- 价值量化（节省多少时间 / 减少多少步骤 / 解决多少比例的问题）

如果这是纯技术/基础设施变更（对用户不可见），写 "N/A — 后端基础设施变更，用户无感知"。
-->

## 成功标准

<!--
可衡量的指标，上线后用于验证变更是否成功。
每个指标包含：指标名称 + 当前值（如有基线） + 目标值 + 数据来源

示例：
- API Key 配置功能使用率：上线后 2 周内 > 30% 的活跃用户使用
- 手动配 Key 导致的启动失败率：从 当前 ~5% 降至 < 1%
- 测试连接成功率：> 95%

注意：区分"可以测量的"和"有现成数据可以拿到的"——拿不到数据的指标不算指标。
-->

## What Changes

<!--
Describe what will change. Be specific about new capabilities, modifications, or removals.

對於有明確前後對比的行為變更，使用 From/To 格式：

**<Section or Behavior Name>**
- From: <current state / requirement>
- To: <future state / requirement>
- Reason: <why this change is needed>
- Impact: <breaking / non-breaking, who's affected>

多個變更可重複此 block；純新增或純刪除可用簡單列表描述。
-->

## Capabilities

### New Capabilities

<!--
Capabilities being introduced. Replace <name> with kebab-case identifier.
命名規則見 openspec/specs/README.md：使用複合名詞（至少 2 個 word），
例如 `user-auth`、`data-export`、`api-rate-limiting`，不用純單詞。
Each creates specs/<name>/spec.md

每個 capability 建議附加：
- 範圍說明（這個 capability 包含和不包含什麼）
- 依賴於（哪些其他 capability 要先就緒）
-->
- `<name>`: <brief description of what this capability covers>

### Modified Capabilities

<!--
Existing capabilities whose REQUIREMENTS are changing (not just implementation).
Only list here if spec-level behavior changes. Each needs a delta spec file.
Use existing spec names from openspec/specs/. Leave empty if no requirement changes.
-->
- `<existing-name>`: <what requirement is changing>

## Impact

<!--
Affected code, APIs, dependencies, systems.

除技術影響外，也考慮：
- 用戶影響（需要用戶做什麼操作 / 遷移？）
- 文檔影響（需要更新用戶手冊？）
- 支持影響（客服需要知道什麼？）
-->

## 发布策略

<!--
变更如何上线：

- 一次性上线 / 功能开关（Feature Flag） / 灰度发布
- 是否需要配合其他发布
- 建议的发布时间窗口（如：避开业务高峰期）
- 兼容性说明（向后兼容？是否需要数据迁移？）

如果是一次上线且无特殊要求，写 "一次性上线" 即可。
-->

## 回滚方案

<!--
如何回滚变更、回滚的影响、回滚后如何恢复数据。
-->

## 待定事项

<!--
需要利益相关者输入或确认的问题。
每个待定事项包含：问题 + 需要谁决定 + 截止日期

示例：
- [ ] UI 交互细节确认 → 需产品负责人确认，上线前 1 周
- [ ] 第三方服务 SLA 确认 → 需 infra team 确认，上线前 2 周
-->
