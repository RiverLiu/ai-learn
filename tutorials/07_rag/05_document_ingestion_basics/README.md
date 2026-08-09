# 05 文档摄取基础

RAG 不只是 embedding 和向量检索。文档进入知识库前，需要做最基本的读取、清洗、切块准备和来源标注。

高级教程会系统讲生产数据管道；本章只讲基础项目里必须知道的最小集合。

## 本章要点

- 原始文档要保留来源信息。
- 文本清洗应该克制，不能把关键事实删掉。
- 每个 chunk 应该带 metadata。
- 小型知识库也要考虑文档更新和删除。

## 运行

本章不调用模型 API，直接读取 `knowledge_base/` 中的 Markdown 文档：

```bash
uv run tutorials/07_rag/05_document_ingestion_basics/main.py
```

## 最小目录结构

```text
knowledge_base/
├── faq.md
├── pricing.md
└── product_intro.md
```

每个文件至少有：

- 文件名
- 标题
- 正文
- 更新时间或版本

## 读取 Markdown

```python
from pathlib import Path

def load_markdown_files(root: Path):
    docs = []
    for path in sorted(root.glob("*.md")):
        text = path.read_text(encoding="utf-8")
        docs.append({
            "document_id": path.stem,
            "source": str(path),
            "text": text,
        })
    return docs
```

## 基础清洗

可以做：

- 去掉首尾空白。
- 合并连续空行。
- 统一换行。
- 删除明显无意义的导航文字。

不要轻易做：

- 删除重复出现的价格、限制条件。
- 删除表格。
- 删除看似啰嗦但可能影响答案的条款。

示例：

```python
def clean_text(text: str) -> str:
    lines = [line.rstrip() for line in text.splitlines()]
    cleaned = []
    previous_blank = False
    for line in lines:
        blank = not line.strip()
        if blank and previous_blank:
            continue
        cleaned.append(line)
        previous_blank = blank
    return "\n".join(cleaned).strip()
```

## Metadata

每个 chunk 建议至少带：

```json
{
  "chunk_id": "pricing:0001",
  "document_id": "pricing",
  "source": "knowledge_base/pricing.md",
  "chunk_index": 1,
  "title": "云雀笔记价格说明"
}
```

metadata 的价值：

- 回答时展示出处。
- 调试时知道命中了哪个文档。
- 文档更新后能删除旧 chunk。
- 未来做权限过滤时有字段基础。

## 来源引用

RAG 回答不应该只说：

```text
根据知识库，专业版每月 29 元。
```

更好的输出：

```text
专业版每月 29 元。[pricing.md]
```

用户可以检查来源，开发者也能定位错误。

## 文档更新

即使是基础项目，也要记住：

```text
文档变了 → chunk 变了 → embedding 也要重算
```

如果旧向量还留在索引里，模型可能回答过期信息。

## 与高级教程的关系

本章是最小版本。生产项目请继续学习：

- [advanced/02_knowledge_engineering](../../../advanced/02_knowledge_engineering/)
- [advanced/03_production_rag](../../../advanced/03_production_rag/)

## 练习

为 `knowledge_base/pricing.md` 设计 3 个 chunk，并为每个 chunk 写出：

- `chunk_id`
- `document_id`
- `source`
- `title`
- `chunk_index`
- `text`
