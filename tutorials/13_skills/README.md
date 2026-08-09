# Skills 教程

Skills 是把某一类任务的**领域知识、操作流程、工具脚本、参考资料和模板资产**封装成一个可复用能力包。
在 AI 应用开发里，它解决的是一个很现实的问题：同一个 Agent 每次面对类似任务时，不应该重新摸索流程、
重新查接口文档、重新写容易出错的脚本。

可以把 Skill 理解为给 Agent 准备的“岗位说明书 + 工具箱”。它不是模型参数，也不是一次性的 prompt；
它是一组可被发现、按需加载、能长期维护的工程资产。

## 为什么需要 Skills

随着 Agent 应用变复杂，单靠系统提示词会遇到四个问题：

| 问题 | 表现 | Skill 的作用 |
| --- | --- | --- |
| 系统提示词越来越长 | 所有任务都塞进同一个 prompt，成本高且互相干扰 | 按任务拆成独立技能，触发时再加载 |
| 经验难复用 | 每次都重新告诉 Agent 公司流程、接口约定、文件格式 | 把稳定经验沉淀为 `SKILL.md` 和参考资料 |
| 操作不够可靠 | 重复写脚本、重复拼命令，容易细节出错 | 把确定性步骤放进 `scripts/` |
| 上下文被文档撑爆 | API 文档、业务规则、模板都塞进一次对话 | 用 `references/` 和 `assets/` 做渐进披露 |

Skills 与前面几类能力的关系：

| 能力 | 主要解决什么 | 与 Skill 的关系 |
| --- | --- | --- |
| Prompt | 一次请求如何表达任务 | Skill 可以包含提示词写法和决策流程 |
| Tool Calling | 模型如何调用函数 | Skill 可以教 Agent 何时调用哪些工具 |
| MCP | 应用如何连接外部工具/数据 | Skill 可以描述某个 MCP Server 的使用流程和注意事项 |
| RAG | 如何从知识库检索事实 | Skill 可以说明知识库结构、检索策略和引用规范 |
| Agent Memory | 如何保存用户/任务历史 | Skill 更偏“长期可维护的工作方法”，不依赖单个用户会话 |

## 一个 Skill 的最小结构

典型目录如下：

```text
my-skill/
├── SKILL.md
├── agents/
│   └── openai.yaml
├── scripts/
│   └── helper.py
├── references/
│   └── api.md
└── assets/
    └── template.md
```

只有 `SKILL.md` 是必需的，其它目录按需添加。

### `SKILL.md`

`SKILL.md` 是 Skill 的入口，包含两部分：

```markdown
---
name: my-skill
description: Explain what this skill does and exactly when Codex should use it.
---

# My Skill

Use these steps when...
```

- `name`：技能名称，建议使用小写字母、数字和连字符，例如 `pdf-editor`、`brand-report`。
- `description`：触发说明。它决定 Agent 什么时候会选择这个 Skill，要写清楚“做什么”和“何时使用”。
- 正文：Agent 真正使用 Skill 时读取的操作指南。

一个常见误区是把 `description` 写得很短，例如 “PDF skill”。这会导致触发不稳定。更好的写法是：

```yaml
description: Create, inspect, split, merge, rotate, redact, and extract content from PDF files. Use when the user asks Codex to modify PDF documents, preserve document formatting, process scanned pages, or automate repeated PDF workflows.
```

### `references/`

放“需要时才读”的详细资料，例如：

- API 文档摘要
- 数据库表结构
- 业务术语和规则
- 公司内部流程
- 大量示例和边界情况

`SKILL.md` 不应该复制这些长文档，而应该写清楚什么时候读哪个文件：

```markdown
For billing questions, read `references/billing.md`.
For data warehouse schema, read `references/schema.md`.
```

这就是 Skills 的核心设计原则：**渐进披露**。元数据常驻上下文，`SKILL.md` 触发后加载，长资料按需加载。

### `scripts/`

放可执行脚本，适合以下场景：

- 步骤固定、容易写错
- 需要稳定输出
- 经常重复执行
- 大段代码不值得每次由 Agent 重写

例如 PDF 旋转、CSV 清洗、生成项目骨架、调用内部 API、验证配置等。

脚本应当具备：

- 明确的命令行参数
- 清晰的错误信息
- 可重复运行
- 对输入文件和输出文件的边界检查

### `assets/`

放生成结果会用到的模板或静态资源，例如：

- 文档模板
- 前端项目模板
- 品牌图片、字体、图标
- 示例配置文件

这些文件不一定要读入上下文；Agent 可以复制、修改或作为输出素材使用。

### `agents/openai.yaml`

这是面向界面展示的元数据，例如显示名、简短介绍、默认提示语。它不应该承载核心执行逻辑。
核心逻辑仍然写在 `SKILL.md` 和资源目录里。

## 章节目录

1. [01_anatomy](./01_anatomy/)：拆解 Skill 的文件结构、触发机制与渐进披露
2. [02_design_workflow](./02_design_workflow/)：从真实任务设计一个可维护 Skill
3. [03_runtime_loading](./03_runtime_loading/)：用 Python 模拟“发现 Skill → 匹配请求 → 加载说明”
4. [04_quality_checklist](./04_quality_checklist/)：上线前检查清单、常见坏味道和迭代方法

## 学习目标

学完本模块后，你应该能做到：

- 判断什么时候应该写 Skill，什么时候只需要 prompt、工具或文档。
- 设计稳定的 `description`，让 Agent 在正确场景触发 Skill。
- 把核心流程、参考资料、脚本和资产拆到合适位置。
- 避免把 Skill 写成臃肿 README。
- 为自己的团队沉淀可复用的 AI 工作流。

## 与本教程其它模块的学习顺序

建议先学：

- [Prompt](../06_prompt/)：理解指令结构和输出约束。
- [Tool Calling](../09_langchain/05_tools/)：理解模型如何申请调用外部函数。
- [MCP](../12_mcp/)：理解工具和数据源如何标准化接入。
- [Deep Agents](../14_deepagents/)：理解长任务 Agent 为什么需要规划、文件系统和子代理。

Skills 适合放在 MCP 和 Deep Agents 之后学习，因为它更偏“把经验产品化”的工程实践。

## 参考

- Codex Skills 本地规范：`SKILL.md` + `references/` + `scripts/` + `assets/`
- MCP 教程：[../12_mcp](../12_mcp/)
- Deep Agents 教程：[../14_deepagents](../14_deepagents/)
