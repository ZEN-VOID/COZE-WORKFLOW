## 项目概述
- **名称**: COZE-WORKFLOW
- **目标**: 维护一个面向扣子工作流开发的项目仓库，沉淀可复用的工作流目录结构、配置体系、节点模板、运行脚本与开发规范
- **当前状态**: 根目录负责定义仓库级约束与协作规则；`examples/` 提供一套可运行的工作流模板与配置样例

## 目录说明
| 路径 | 用途 |
|---|---|
| `examples/` | 工作流模板示例、配置样例、脚本与代码骨架 |
| `projects/` | 已开发完成或持续迭代的具体项目目录，支持多个项目并存 |
| `.codex/` | 本地 Codex 命令与配置，不作为业务实现目录 |
| `AGENTS.md` | 仓库级说明与协作约束（本文件） |

## 仓库定位
- 本仓库优先沉淀“模板能力”，而不是只实现单一业务流
- 所有新增内容尽量抽象为可复用的配置、脚本、节点模板或文档规范
- 具体业务项目统一沉淀在 `projects/` 目录下，避免与模板示例混放
- 若新增功能仅适用于某一个具体工作流，应优先放入示例或单独子目录，而不是直接污染公共模板

## 项目存放约定
- 开发好的具体项目统一存放在 `projects/` 目录下
- `projects/` 下支持多个项目并存，推荐采用 `projects/<project_name>/` 的结构
- `examples/` 用于模板、样例和可复用骨架；`projects/` 用于真实项目实现与持续迭代
- 新建具体项目时，应优先从 `examples/` 中复制或抽取模板能力，再按项目独立落地

## 多项目操作规则
- 当用户指定某个具体项目时，所有开发、修改、排查、验证操作默认仅在对应项目子目录内进行
- 当仓库中存在多个项目而用户未明确指定目标项目时，若任务存在歧义，应先要求明确项目名称或路径
- 跨项目的公共能力变更，应优先沉淀到模板层或仓库级规则，而不是只修改单个项目后结束
- 修改 `projects/` 下文件时，需同时检查是否应将通用经验回流到 `examples/`、公共脚本或根级规范

## 配置设计原则
- 优先采用**配置驱动**，避免把环境差异、模型参数、存储策略硬编码到代码中
- 配置优先分层为：
  1. 环境变量 / CLI 参数
  2. 环境级配置
  3. 基础默认配置
- Agent 节点配置必须独立存放，至少包含 `config`、`sp`、`up`、`tools`
- 图结构、节点映射、边关系应尽量通过独立配置描述，而不是散落在代码常量中

## 开发约束
- 优先做最小、聚焦的改动，避免顺手重构无关模块
- 修改模板能力时，要同步检查：
  - 运行脚本是否仍可用
  - 文档是否仍准确
  - 示例配置是否仍匹配代码行为
- 若修改 `examples/` 下文件，必须同时遵守 `examples/AGENTS.md` 中的更细粒度规则
- 更深层目录若存在额外 `AGENTS.md`，以更深层规则为准

## 工作流模板约定
- 新增工作流能力时，优先补齐以下内容：
  - 状态定义
  - 节点实现
  - 节点配置
  - 图定义
  - 运行脚本
  - 配套文档
- 新增 Agent 节点时，不要直接把提示词或模型参数硬编码进节点函数
- 新增基础设施能力时，优先提供本地开发兜底方案，例如：
  - `.env.example`
  - 配置校验脚本
  - memory fallback
- 若能力已在多个 `projects/` 项目中重复出现，应考虑提升为模板能力或公共约束

## 文档维护要求
- 当仓库结构、配置路径、运行命令发生变化时，必须同步更新 README 或对应说明文件
- 示例命令中的字段名、配置路径、脚本参数必须与实际代码一致
- 若某个目录已由独立 `AGENTS.md` 详细描述，根级文档只保留总览与跨目录规则，避免重复维护

## 推荐协作方式
- 做改动前先确认影响范围：根级规则、模板代码、示例代码、脚本、文档
- 做改动后优先执行最小必要验证
- 如果缺少依赖或外部环境，需明确说明哪些已验证、哪些尚未验证

## 当前建议重点
- 持续完善根目录下的模板化能力，而不是只扩展示例业务
- 后续如新增正式模板目录，可将 `examples/` 的成熟结构抽出为通用脚手架

## Agent-Specific Instructions

- Default interaction language is Chinese unless a task requires English output.

### Trinity Auto-Sync Mechanism

- `AGENTS.md`, `CLAUDE.md`, and `GEMINI.md` form a trinity of global core configuration files.
- Whenever a rule is modified, added, or removed in any one of these three files, the same change **must be automatically** synchronized and applied to the other two files to ensure that their core content remains strictly consistent.

### Root-Cause First (Mandatory)

- When the user reports an issue in a project or task execution, investigate the source-layer cause first before applying local content fixes.
- Source-layer diagnosis should prioritize rule artifacts and execution entrypoints, typically `SKILL.md`, `CONTEXT.md`, command runbooks, and related scripts.
- Source-layer traceability is **layered and mandatory**: do not stop at the first local cause; climb upward until the governing rule source is identified.
- Required layered trace chain (`层层上溯`) for non-trivial issues:
  - `Symptom/Failure` -> `Direct Technical Cause` -> `规则源` (skill/runbook/template/script gate) -> `规则源的规则源` (meta-AGENT/meta-SKILL/global policy) -> `Fix Landing Points`.
- `规则源` typically includes: task-level `SKILL.md`, command runbooks, stage templates, validation scripts, and execution entrypoints.
- `规则源的规则源` typically includes: repository `AGENTS.md`, `.codex/skills/meta/*/SKILL.md`, and other cross-skill governance contracts.
- If diagnosis cannot be escalated to meta-layer artifacts, explicitly state why no higher governing contract exists.
- For each issue, provide a concise remediation proposal that includes: root cause location, immediate fix, and systemic prevention fix.
- Prefer fixing the rule/script that generated the error pattern, so the same class of issues is prevented in subsequent runs.
- Treat every non-trivial fix as an opportunity for **source-layer enhancement** (`源层增强`): not only patch the symptom, but harden the source contract so similar failures become less likely.
- Recommended enhancement targets (pick one or more): explicit gates/diagnostics (clear error states, non-zero exits, actionable messages), fallback/retry for unstable dependencies (network/API/schema variance), refactor duplicated logic into a single source of truth (config/entrypoint/shared helper), and contract clarification in `SKILL.md` / runbooks.
- Enhancement-complete closure should satisfy: issue fixed + at least one reusable prevention mechanism at source layer + related docs/contracts updated.
- If enhancement is blocked (permissions, external dependency, scope constraints), explicitly report blocker + temporary guardrail.

### Root-Cause Learning Loop Automation (Mandatory)

- Trigger automatically when any of these happen: user-reported issue, runtime failure, rework after failed output, or explicit correction request.
- Execute the following loop without waiting for extra user prompting:
  1. Source diagnosis (`层层上溯`): trace from symptom to direct cause, then to `规则源`, then to `规则源的规则源` (`AGENTS.md` / meta-SKILL) when applicable.
  2. Immediate fix + enhancement: patch the highest-leverage source-layer artifact first (rule/script/runbook/meta-rule), and add at least one reusable hardening mechanism; then apply local content fix only if still needed.
  3. Context deposition: update the affected skill's `CONTEXT.md` (create if missing) using `meta/skill-context` structure; prefer updating Type Map / Playbook / reusable heuristics first, and append a new Case Record only for milestone-grade events (new failure type, source-contract change, or promotion evidence).
  4. Prevention promotion (`自下而上的革命`): promote validated fixes from local output -> `CONTEXT.md` -> `SKILL.md` / runbook -> `AGENTS.md` or meta-SKILL when cross-skill recurrence is observed.
  5. User-facing closure: always return the triad (`root cause location + immediate fix + systemic prevention fix`) plus the layered trace path (`symptom -> rule source -> meta rule source`).
- Case Record minimum fields (required, when creating/updating a case): symptom, root cause, final fix, prevention checklist, evidence paths, user feedback/constraint.
- `Root-Cause First` is considered incomplete if only local output is fixed but `CONTEXT.md` is not updated; if update is blocked, explicitly report the blocker.

### Bottom-Up Evolution Contract (Mandatory)

- Treat frontline execution failures as system-improvement signals, not isolated noise.
- System upgrades must be practice-driven (`在实践中升级迭代系统`): every promoted rule needs execution evidence (logs, failing case, fixed case, verification output).
- Promotion ladder:
  1. Local patch proves immediate recovery.
  2. Skill-layer contract update prevents same pattern in that skill.
  3. Meta-layer contract update (`AGENTS.md` / meta-SKILL) is required when the pattern is cross-skill or repeatedly observed.
  4. Validation/runbook checks are updated to make regression detectable.
- Repeated-pattern incidents must not be closed as local-only fixes unless a blocker is explicitly recorded.

### Field-Centric Thought-Pass System (Mandatory)

- Any skill that uses a thought chain (`思维链`), output template/contract (`输出模板/输出约定`), and quality scoring or pass gates (`质量评估/门禁/通过制`) must use **one field schema as the single source of truth**.
- Required principle: **思维链设计、输出落点、质量打分、通过判定、返工入口，必须围绕同一套 `field_id` 字段集合展开**；禁止各自发明第二套对象命名。
- The canonical three-stage chain is:
  1. **字段定义**: define `field_id`, where it lands, and what concrete content it must contain.
  2. **思维导引**: every `step_id` must serve one or more `field_id`, and explain how those fields are produced.
  3. **质量通过**: every `field_id` must have a `quality_dimension`, `pass_standard`, `fail_code`, and `rework_entry`.
- Canonical identifiers:
  - `field_id`: the canonical field/output unit; this is the primary axis of the system.
  - `step_id`: the thought-chain step that serves one or more `field_id`.
  - `quality_dimension`: the quality dimension used to audit a `field_id`.
  - `pass_standard`: the concrete passing threshold/check for a `field_id`.
  - `fail_code`: the stable failure code when a `field_id` fails.
  - `rework_entry`: the exact step/strategy/file entry used to repair a failed `field_id`.
  - `slot_id`: legacy alias only when a `field_id` is literally an output slot; it must not replace `field_id` as the canonical key.
- `SKILL.md` must include the following artifacts, either in canonical numbered sections or in an equivalent dedicated section for legacy skills:
  - A field master table with header: `field_id | 输出位置/字段 | 内容要求 | 证据来源 | 默认责任Step | 质量维度 | 失败码`.
  - A thought guide table with header: `step_id | 聚焦字段(field_id) | 核心问题 | 生成动作 | 未达标信号`.
  - A pass table with header: `field_id | 质量维度 | 通过标准 | 失败码 | 返工入口`.
- If a skill has **no fixed template**, it is still not exempt: `field_id` may point to Markdown headings, paragraph blocks, generated files, routing manifests, state keys, logs, or other concrete output anchors.
- Hard failure conditions:
  - a `step_id` does not serve any `field_id`;
  - a `quality_dimension` cannot be traced back to a `field_id`;
  - a `field_id` lacks a `pass_standard`, `fail_code`, or `rework_entry`;
  - the skill creates a parallel second taxonomy for thought or scoring that does not map back to the canonical `field_id` set.
- Retrofit rule for maintained skills:
  - Keep the skill's original thought-chain design as the primary execution contract.
  - Align quality scoring **inside the existing quality/loop section** to that original chain.
  - Do **not** append a second parallel “supplementary framework” section that competes with the original thought chain.
- New skills should use the canonical structure directly; maintained legacy skills may comply by appending an equivalent dedicated section before full renumbering/refactor.

### AGENT vs SKILL vs CONTEXT Placement Matrix (Global Canonical)

- Put in `AGENTS.md` / meta-SKILLs (normative meta contract):
  - Cross-skill root-cause escalation order (`规则源 -> 规则源的规则源`).
  - Promotion criteria from local fixes to global policy.
  - Repository-wide hard gates, closure format, and anti-regression requirements.
  - Canonical identifiers and mandatory table headers for the field-centric thought-pass system.
- Put in `SKILL.md` (normative contract):
  - Trigger conditions, mandatory workflow, hard gates, and completion criteria.
  - Source-layer diagnosis order and remediation order (including upward link to meta contracts).
  - Required user-facing closure format (root cause location + immediate fix + systemic prevention fix).
  - Promotion rules from experience to norm (when a repeated pattern is eligible to be promoted).
  - Skill-specific `field_id` master definitions, plus `step_id -> field_id` and `field_id -> quality_dimension -> fail_code -> rework_entry` mappings.
- Put in `CONTEXT.md` (empirical memory):
  - Type maps (failure pattern -> fix strategy -> verification point), repair playbooks, and reusable heuristics.
  - Case records with evidence from real executions (milestone-grade, low-frequency; avoid progress-log noise).
  - Runtime pitfalls, compatibility quirks, and successful recovery tactics.
  - Promotion candidates backlog (patterns observed but not yet stable enough for `SKILL.md`).
- Conflict policy remains: user explicit request > `AGENTS.md` / meta-SKILL > `SKILL.md` > `CONTEXT.md`.

### Repository Rollout Standard (Mandatory)

- Every maintained skill should include:
  - In `SKILL.md`: a Root-Cause execution contract section aligned with this global policy, including upward trace hooks to meta-layer contracts.
  - In `SKILL.md`: a field-centric thought-pass mapping contract, using either canonical numbered sections or an equivalent dedicated legacy-compatible section.
  - In `CONTEXT.md`: a Case Log section aligned with `meta/skill-context` record structure.
  - In `CONTEXT.md`: a knowledge-base core (Type Map and/or Playbook and/or reusable heuristics).
- New skills generated by meta skills must initialize both `SKILL.md` and `CONTEXT.md` with the above baseline.
- Validation scripts/runbooks should check the presence of these baseline sections and the upward-trace clause to prevent policy drift.

### CONTEXT Health Monitoring (Mandatory)

- Every `CONTEXT.md` should contain an auto-maintained `Context Health` section.
- Health thresholds (default baseline):
  - `soft_limit_chars: 40000`, `hard_limit_chars: 80000`
  - `soft_limit_cases: 80`, `hard_limit_cases: 140`
- Action policy:
  - `ok`: keep target-scoped knowledge updates (Type Map/Playbook first); append cases only when milestone criteria are met.
  - `warn`: schedule targeted compaction for that specific skill context.
  - `warn` with case-poor long docs: perform manual curation (section merge/split/extract) instead of case-only compaction.
  - `critical`: compact + archive before continuing large append operations.
- Compaction must preserve evidence integrity:
  - Keep recent active cases in `CONTEXT.md`.
  - Archive older cases under `reports/context-archive/` with traceable index links.
- Default operation should be target-scoped (single skill context), not whole-repo rewrite, unless explicitly requested.

### CONTEXT Knowledge-Base Mode (Mandatory)

- `CONTEXT.md` default mode is knowledge-base, not chronological diary.
- Prefer maintaining:
  - Type Map: failure type -> root cause layer -> immediate fix -> systemic prevention -> verification.
  - Repair Playbook: stable troubleshooting order and fallback strategy.
  - Reusable Heuristics: concise high-value经验条目.
- Case Log frequency control:
  - Add/append a case only for milestone events (new error class, source-rule change, repeated-pattern promotion).
  - Non-milestone iterations should update existing Type Map/Playbook/Heuristics entries instead of creating new cases.
- Prohibited low-value records:
  - Progress narration, cosmetic rewrites, and one-off noisy notes without reusable prevention value.

## Skill Composition & Semantics

- Skill directory baseline:
  - `SKILL.md`: required, canonical execution spec.
  - `CONTEXT.md`: recommended, preloaded operational context.
  - Optional: `scripts/`, `templates/`, `references/`, `assets/`.
- `SKILL.md` role (hard rules):
  - Defines scope, trigger conditions, required inputs, strict workflow, tool/script entrypoints, output contract, and quality gates.
  - Must be deterministic and action-oriented; avoid long narrative and avoid storing transient tips.
- `CONTEXT.md` role (experience layer):
  - Stores reusable heuristics: success/failure cases, pitfalls, debugging cues, compatibility notes, prompt techniques, and tactical shortcuts.
  - Serves as preloaded context for planning/execution, but does not redefine the core contract.
- Runtime loading order and priority:
  1. Parse `SKILL.md` first to lock mandatory constraints.
  2. Load `CONTEXT.md` to choose strategy and avoid known failure patterns.
  3. Conflict resolution: user explicit request > `SKILL.md` > `CONTEXT.md`.
- Maintenance rules:
  - New or uncertain经验先写入 `CONTEXT.md`.
  - Stable, repeatable, high-confidence practices are promoted from `CONTEXT.md` to `SKILL.md`.
  - For each notable failure, record in `CONTEXT.md` with: symptom, root cause, fix, and prevention check.
  - Keep `SKILL.md` concise and normative; keep `CONTEXT.md` accumulative and empirical.
