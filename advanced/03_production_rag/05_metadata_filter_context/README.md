# 05 Metadata Filter 与上下文组装

metadata filter 是生产 RAG 的安全基础。权限、租户、语言、版本、文档状态都应该在检索前过滤，不能靠 prompt 告诉模型“不要看不该看的资料”。

过滤之后，还要把候选 chunk 组装成稳定、可引用、低噪声的上下文。

## 为什么 filter 必须在检索前

RAG 的权限问题不能交给 LLM 判断。错误做法是：

```text
先检索所有文档 -> 把结果给模型 -> 在 prompt 里写“不要泄露无权限内容”
```

这样模型实际上已经看到了敏感内容。正确做法是：

```text
用户身份 -> 构造 metadata filter -> 只在允许的文档范围内检索
```

也就是说，权限边界应该在检索系统里完成，而不是在生成阶段补救。

## 运行

```bash
uv run advanced/03_production_rag/05_metadata_filter_context/main.py
```

## 本章要点

- `tenant_id` 和 `permission_group` 用于防止越权检索。
- `document_status` 和 `updated_at` 用于排除旧文档。
- 同一文档相邻 chunk 可以合并或去重。
- 每段上下文应该有稳定引用编号和来源 metadata。

## 常见 metadata 字段

| 字段 | 示例 | 用途 |
| --- | --- | --- |
| `tenant_id` | `tenant_a` | 多租户隔离 |
| `permission_group` | `employee`、`admin` | 权限过滤 |
| `document_status` | `active`、`archived` | 排除旧文档 |
| `updated_at` | `2026-07-01` | 处理新旧政策冲突 |
| `document_type` | `pricing`、`faq`、`contract` | 按问题类型选择资料 |
| `locale` | `zh-CN`、`en-US` | 多语言过滤 |
| `product` | `notes`、`drive` | 多产品知识库隔离 |
| `source` | `pricing.md` | 引用和排查 |

## 过滤示例

一个普通员工访问企业知识库时，过滤条件可能是：

```python
filters = {
    "tenant_id": current_user.tenant_id,
    "permission_group": {"$in": current_user.groups},
    "document_status": "active",
    "locale": "zh-CN",
}
```

这意味着：

- 其他租户的文档不能被检索。
- 用户不属于的权限组不能被检索。
- 已归档文档不能被检索。
- 不同语言版本不会混在一起。

## 推荐上下文格式

```text
[S1 source=pricing.md doc=pricing updated=2026-07-01]
企业版支持 SSO、审计日志和专属客户成功经理。
```

这样模型可以按 `S1`、`S2` 引用，开发者也能回查原始资料。

## 上下文组装要做什么

检索和过滤之后，不要把所有 chunk 原样拼进 prompt。上下文组装通常要做：

1. **去重**：同一段内容可能被多路检索召回。
2. **合并相邻块**：同一文档连续 chunk 可以合并，避免上下文断裂。
3. **排序**：优先放高相关、高权威、更新日期新的内容。
4. **截断**：控制 token 成本，只保留必要证据。
5. **编号**：给每段上下文稳定编号，例如 `S1`、`S2`。
6. **保留来源**：保存 `source`、`page`、`updated_at`、`chunk_id`。

## 冲突处理

生产知识库经常有新旧政策冲突：

```text
旧文档：团队版支持 SSO。
新文档：个人版和团队版不包含 SSO。
```

处理原则：

- 检索前用 `document_status=active` 排除旧文档。
- 上下文里保留 `updated_at`，让模型知道资料新旧。
- 如果两个 active 文档冲突，不要让模型猜，应该返回“资料冲突，需要人工确认”或按业务优先级选择权威来源。

## 运行后观察点

脚本会先打印未过滤候选，你会看到：

- 归档旧政策。
- 当前用户有权限的新政策。
- 当前用户无权限的内部路线图。
- 其他租户的定制合同。

metadata filter 后只保留当前用户可见、状态 active、租户匹配的 chunk。

## 常见错误

- 检索后才做权限过滤，导致日志或中间上下文泄露敏感内容。
- 文档更新后只新增新 chunk，不删除或归档旧 chunk。
- metadata 只有 `source`，没有权限、版本、语言等字段。
- 引用只显示文件名，不显示页码、chunk_id 或更新时间。
- context packing 只按相似度截断，忽略权威来源和新旧版本。

## 练习

1. 把 `CURRENT_USER["groups"]` 改成只包含 `employee`，确认 `executive` 文档不会出现。
2. 把旧政策的 `document_status` 改成 `active`，观察上下文里是否出现冲突。
3. 给 chunk 增加 `document_type`，只允许查询价格问题时检索 `pricing` 类型。
