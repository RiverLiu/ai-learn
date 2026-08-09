# 01 Skill 结构拆解

本章从一个最小 Skill 开始，理解 Agent 如何发现它、何时加载它，以及为什么不能把所有内容都塞进一个大文件。

## 本章要点

- Skill 的本质是一个目录，必需文件是 `SKILL.md`。
- `SKILL.md` 的 YAML frontmatter 决定发现和触发，正文决定执行方式。
- `references/`、`scripts/`、`assets/` 分别服务于知识、确定性操作和输出素材。
- 好 Skill 的关键不是“写得多”，而是“该出现的信息在正确时机出现”。

## 最小 Skill

```text
csv-cleaner/
└── SKILL.md
```

`SKILL.md`：

```markdown
---
name: csv-cleaner
description: Clean, validate, normalize, and summarize CSV files. Use when the user asks Codex to inspect tabular data, fix malformed rows, normalize column names, detect missing values, or produce cleaned CSV outputs.
---

# CSV Cleaner

When cleaning CSV files:

1. Inspect the header and delimiter first.
2. Preserve the original file unless the user explicitly asks to overwrite it.
3. Write cleaned output to a new file.
4. Report row counts, changed columns, dropped rows, and unresolved anomalies.
```

这个 Skill 已经可以工作，但能力有限：所有步骤都靠 Agent 临场执行，缺少可复用脚本和详细规则。

## 完整一些的 Skill

本章已经把这个示例写成真实文件，见 [csv-cleaner/SKILL.md](./csv-cleaner/SKILL.md)。

```text
csv-cleaner/
├── SKILL.md
├── scripts/
│   └── profile_csv.py
└── references/
    └── column_rules.md
```

`SKILL.md` 可以保持简洁：

```markdown
---
name: csv-cleaner
description: Clean, validate, normalize, and summarize CSV files. Use when the user asks Codex to inspect tabular data, fix malformed rows, normalize column names, detect missing values, or produce cleaned CSV outputs.
---

# CSV Cleaner

Start by running `scripts/profile_csv.py` on the input file to inspect delimiter, headers, row count,
missing values, and suspicious columns.

For project-specific column naming rules, read `references/column_rules.md`.

Never overwrite the source CSV unless the user explicitly asks for it.
```

这样拆分后，常驻上下文只保留路线图；真正的大规则和确定性检查放到资源里。

## Frontmatter 设计

Frontmatter 是 Skill 的入口：

```yaml
---
name: skill-name
description: Trigger guidance...
---
```

### `name`

推荐规则：

- 小写字母、数字、连字符。
- 简短，最好能表达动作或领域。
- 不要使用空格、中文标点或过长短语。

示例：

| 好名称 | 问题名称 | 原因 |
| --- | --- | --- |
| `pdf-editor` | `PDF超级工具` | 非 ASCII 与语义不稳定 |
| `brand-report` | `report` | `report` 太泛，容易误触发 |
| `github-pr-review` | `my-skill-v2-final` | 后者不是面向任务的名称 |

### `description`

`description` 是触发器。它应该回答两个问题：

- 这个 Skill 能做什么？
- 用户怎么说时应该用它？

坏例子：

```yaml
description: Helps with reports.
```

问题是太宽泛。Agent 不知道是财报、周报、实验报告、Markdown 报告还是 PPT 报告。

好例子：

```yaml
description: Create weekly product analytics reports from event metrics, experiment notes, and dashboard exports. Use when the user asks for product growth weekly reports, metric interpretation, experiment summaries, or executive-ready product analytics narratives.
```

它同时覆盖了能力范围和触发场景。

## 正文写法

Skill 正文应该像给另一个工程师写操作手册，而不是写市场介绍。

推荐包含：

- 执行顺序
- 重要约束
- 何时读取参考资料
- 何时运行脚本
- 输出格式要求
- 常见失败和处理方式

不推荐包含：

- 大段背景故事
- Agent 已经知道的通用常识
- 与执行无关的 README、安装指南、变更日志
- 大量复制粘贴的 API 文档

## 渐进披露

Skills 的加载通常分三层：

| 层级 | 何时出现 | 内容 |
| --- | --- | --- |
| 元数据 | 始终可见 | `name` 和 `description` |
| `SKILL.md` 正文 | Skill 触发后 | 核心流程和资源导航 |
| 资源文件 | 需要时 | 详细参考、脚本、模板、资产 |

这能降低上下文成本，也能减少无关信息干扰。

一个好的 `SKILL.md` 会像目录和工作流，不会像资料库本体：

```markdown
For Salesforce schema questions, read `references/salesforce_schema.md`.
For billing policy questions, read `references/billing_policy.md`.
For generating a customer-ready report, copy `assets/customer_report_template.md`.
```

## 与工具的区别

Skill 不是 Tool。

| 维度 | Skill | Tool |
| --- | --- | --- |
| 形态 | 文档、脚本、参考资料、模板组成的能力包 | 一个可调用函数或外部接口 |
| 触发 | Agent 根据任务选择加载 | 模型在推理中申请调用 |
| 作用 | 教 Agent 怎么做一类任务 | 执行一个具体动作 |
| 示例 | “如何处理公司报销单” | `submit_expense(amount, category)` |

二者经常配合使用：Skill 负责说明什么时候该用哪个工具、参数怎么填、结果如何解释。

## 练习

为“课程作业批改”设计一个 Skill 目录结构，至少包含：

- `SKILL.md`
- 一个 `references/` 文件，说明评分标准
- 一个 `scripts/` 脚本，统计作业提交文件
- 一个 `assets/` 模板，用于生成反馈报告

重点不是写完整实现，而是说明哪些内容放在入口，哪些内容延迟加载。
