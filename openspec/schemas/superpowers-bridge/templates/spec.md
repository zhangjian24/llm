<!--
Delta spec template for a change.

此模板示範 4 種 delta section，按實際需要取用：
- ADDED / MODIFIED / REMOVED / RENAMED
檔名與位置：openspec/changes/<change-name>/specs/<capability>/spec.md
（`<capability>` 對齊 openspec/specs/<capability>/ 目錄名）

格式硬規則（OpenSpec 會 validate）：
- Requirement 句子 MUST 含 `SHALL` 或 `MUST`
- 每個 Requirement MUST 至少有一個 `#### Scenario:`
- Scenario MUST 用 level-4 (`####`)，level-3 或 bullet 會 silent fail

### 元数据字段说明

以下字段可选，按需填写，不填不影響 parse：

- **User Story**: As a <角色>, I want <功能> so that <价值>
- **Priority**: P0(缺了不能上线) / P1(重要可延期) / P2(锦上添花)
- **Acceptance**: 一句话描述需求完整性的可验证标准
- **Non-functional**: 性能/安全/可观测性约束

### 场景覆盖指引

每个 Requirement 的场景建议覆盖以下状态（按复杂度取舍）：
- **正常态**：核心流程走通
- **异常态**：无效输入、服务拒绝、故障
- **边界态**：长度限制、并发、数据边界
- **空态**：无数据、初始状态
- **加载态**：异步操作的中间状态

建议最低覆盖：
- 简单 CRUD：正常 + 异常
- 涉及数据展示：正常 + 异常 + 空态
- 涉及 API 调用：成功 + 失败 + 超时/异常

GIVEN 前置条件可選：
若 Scenario 需要前置条件，正文第一行可用 `GIVEN <条件>` 描述。
簡單場景可直接從 WHEN 開始。
-->

## ADDED Requirements

<!-- 新增行為。列出本 change 要加到 capability 的新 Requirement。 -->

### Requirement: <!-- requirement name -->

<!-- 可选元数据 -->
<!-- **User Story**: As a ..., I want ... so that ... -->
<!-- **Priority**: P0 -->
<!-- **Acceptance**: ... -->
<!-- **Non-functional**: ... -->

<!-- requirement text — 須含 SHALL 或 MUST -->

#### Scenario: <!-- scenario name -->
- **WHEN** <!-- condition -->
- **THEN** <!-- expected outcome -->

---

## MODIFIED Requirements

<!--
修改既有 Requirement。**MUST 使用與 openspec/specs/<capability>/spec.md
完全相同的 normalized header**（trim 後 case-sensitive 比對），否則 archive
時的 delta apply 會因找不到對應 requirement 而失敗。

**MUST 貼出修改後的完整內容**（不是只寫 diff），因為 OpenSpec archive
是用全文替換的方式 apply MODIFIED。
-->

### Requirement: <!-- 與既有 spec 中相同的 header -->

<!-- 可选元数据（如需更新） -->
<!-- **User Story**: ... -->
<!-- **Priority**: ... -->
<!-- **Acceptance**: ... -->
<!-- **Non-functional**: ... -->

<!-- 修改後的完整 requirement text — 含 SHALL 或 MUST -->

#### Scenario: <!-- scenario name（可新增、可修改） -->
- **WHEN** <!-- condition -->
- **THEN** <!-- expected outcome -->

---

## REMOVED Requirements

<!--
刪除既有 Requirement。MUST 包含 Reason 與 Migration 說明，讓 reviewer
理解為何廢除以及既有引用方該怎麼遷移。
-->

### Requirement: <!-- 要刪除的 header，與既有 spec 完全相同 -->

**Reason**: <!-- 為何廢除 -->

**Migration**: <!-- 既有呼叫方/依賴方應如何調整 -->

---

## RENAMED Requirements

<!--
重新命名 Requirement header。格式固定：FROM / TO 用 code-fence header。
若名稱變更 + 內容變更，**同時**在 RENAMED 列出名字變更，並在 MODIFIED
用**新的** header 再寫一份完整內容。

archive 時 apply 順序：RENAMED → REMOVED → MODIFIED → ADDED
-->

- FROM: `### Requirement: <Old Name>`
- TO: `### Requirement: <New Name>`
