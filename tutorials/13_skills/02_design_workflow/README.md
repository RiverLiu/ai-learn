# 02 设计一个可维护 Skill

本章学习从真实任务反推 Skill 内容，而不是先建目录再往里塞材料。

## 本章要点

- 先收集任务样例，再设计 Skill。
- 把任务拆成“判断、流程、知识、脚本、资产”五类。
- 用自由度决定写法：文本说明、伪代码、脚本。
- Skill 应该服务长期复用，不应该成为一次性 prompt 的归档。

## 什么时候该写 Skill

适合写 Skill 的场景：

- 同类任务会重复出现。
- 任务有稳定流程或团队规范。
- Agent 经常需要查同一批文档。
- 输出必须符合固定格式。
- 操作容易出错，适合脚本化。
- 任务跨越多个工具、文件或系统。

不适合写 Skill 的场景：

- 一次性问题，写一句 prompt 就够。
- 规则还没稳定，经常大改。
- 信息非常短，直接放在用户请求里更清楚。
- 任务需要实时数据库或外部 API，但没有权限和工具接入。

## 设计流程

### 1. 写出 3-5 个真实触发请求

不要从抽象能力开始，先写用户会怎么说：

```text
帮我把这个季度的销售 CSV 生成一份 CEO 能看的经营简报。
检查这份合同草案是否符合我们公司的采购条款。
把这批客服聊天记录归类，输出高频问题和建议。
根据这个 OpenAPI 文档生成 FastAPI 客户端封装。
```

这些样例决定 `description` 怎么写，也决定资源目录怎么拆。

### 2. 标出任务中的稳定部分

以“销售经营简报”为例：

| 部分 | 内容 | 放哪里 |
| --- | --- | --- |
| 触发场景 | 销售 CSV、季度报告、CEO 简报 | `description` |
| 固定流程 | 读数据、校验指标、分业务线汇总、写摘要 | `SKILL.md` |
| 指标口径 | ARR、MRR、流失率、续费率定义 | `references/metrics.md` |
| 数据检查 | 缺失值、重复客户、异常金额 | `scripts/check_sales_csv.py` |
| 输出模板 | 简报 Markdown 或 PPT 大纲 | `assets/executive_report.md` |

### 3. 决定自由度

不同内容需要不同程度的约束。

| 自由度 | 适合内容 | 写法 |
| --- | --- | --- |
| 高 | 写作风格、分析角度、开放式判断 | 简短原则和例子 |
| 中 | 推荐流程、决策分支、命令组合 | 步骤列表或伪代码 |
| 低 | 文件转换、校验、批处理、部署 | 脚本和固定参数 |

判断原则：越容易出错、越需要一致性，越应该脚本化。

### 4. 写 `description`

模板：

```text
<动词 + 任务对象 + 结果>. Use when the user asks for <具体触发场景 1>, <触发场景 2>, or <触发场景 3>.
```

示例：

```yaml
description: Generate executive sales performance reports from CRM exports, finance CSVs, and metric notes. Use when the user asks for quarterly sales reviews, CEO-ready revenue summaries, pipeline health analysis, churn and renewal interpretation, or sales metric narrative reports.
```

注意：

- 不要只写 “sales report skill”。
- 不要依赖正文里的 “when to use” 段落，因为正文只有触发后才会读取。
- 覆盖同义表达，例如 report、summary、review、analysis。

### 5. 写 `SKILL.md` 正文

正文建议结构：

```markdown
# Executive Sales Report

## Workflow

1. Inspect input files and identify metric sources.
2. Run `scripts/check_sales_csv.py` for CSV exports.
3. Read `references/metrics.md` before interpreting ARR, MRR, churn, or renewal rate.
4. Draft the report using `assets/executive_report.md`.
5. Call out missing or suspicious data instead of hiding it.

## Output

Return:

- Executive summary
- Metric table
- Key changes
- Risks
- Recommended next actions
```

保持正文短而可执行。详细指标解释放进 `references/metrics.md`。

### 6. 设计资源文件

资源拆分应按“何时需要”组织，而不是按作者习惯组织。

推荐：

```text
references/
├── metrics.md
├── crm_export_schema.md
└── report_style.md
```

不推荐：

```text
references/
├── all_docs_part_1.md
├── all_docs_part_2.md
└── misc.md
```

如果一个参考文件超过 100 行，顶部加目录，方便 Agent 先扫结构再决定是否继续读。

## 坏味道

### `SKILL.md` 太长

表现：正文几百上千行，包含完整 API 文档、教程、FAQ、模板。

改法：把细节拆到 `references/`，在正文里写读取条件。

### 没有明确输出约束

表现：Agent 每次产物格式不一样。

改法：在正文或 `assets/` 模板里定义结构，例如标题、字段、表格列、验收标准。

### 脚本藏在正文里

表现：每次都让 Agent 复制一大段 Python 临时执行。

改法：放进 `scripts/`，正文只保留命令和参数说明。

### `description` 太泛

表现：不该触发时触发，该触发时又没触发。

改法：加入具体名词、动词、输入类型和输出类型。

### 资源目录像资料垃圾桶

表现：文件名含糊，Agent 不知道什么时候读哪个。

改法：按业务场景或任务阶段命名，并在 `SKILL.md` 里显式导航。

## 练习：设计代码审查 Skill

为 “Python FastAPI 代码审查” 设计一个 Skill：

1. 写 5 个触发请求。
2. 写 `description`。
3. 设计目录结构。
4. 决定哪些内容放 `SKILL.md`，哪些放 `references/`。
5. 至少设计一个脚本，例如检查路由是否缺少测试。

参考方向：

```text
fastapi-review/
├── SKILL.md
├── references/
│   ├── security_checklist.md
│   ├── database_patterns.md
│   └── testing_policy.md
└── scripts/
    └── scan_fastapi_routes.py
```
