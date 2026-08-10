# 06 PDF、图片、OCR 与图文检索

很多企业知识库不只是 Markdown 和网页，还包含：

- 可复制文本 PDF
- 扫描 PDF
- 发票、合同、表单图片
- 产品截图
- 图表、流程图、架构图
- 带图片的知识库文章

多模态 RAG 的关键不是“直接把文件丢给大模型”，而是把每个证据变成可检索、可引用、可追溯的记录。

## 先区分两件事

多模态 RAG 里经常混淆两件事：

1. **内容解析**：从 PDF、图片、扫描件里提取文本、表格、图片说明和版面信息。
2. **图文检索**：让用户用文本问题找到图片证据，或用图片找到相关文本证据。

很多业务第一阶段并不需要真正的多模态 embedding。先把图片和 PDF 页面转成高质量 OCR、caption、表格 JSON，再走文本 RAG，已经能解决大量问题。

## 运行

```bash
uv run advanced/03_production_rag/06_multimodal_retrieval/main.py
```

## 三种常见方案

| 方案 | 做法 | 适合场景 | 风险 |
| --- | --- | --- | --- |
| OCR / Caption -> 文本 RAG | 把图片、扫描页、图表转成文本，再走普通 RAG | 快速接入、已有文本 RAG | OCR 错字、caption 漏细节 |
| 多模态 embedding | 文本和图片映射到同一向量空间 | 图文互搜、截图找文档 | 模型效果依赖领域评估 |
| 页面级视觉检索 | PDF 每页当图片检索，如 ColPali 类方案 | 复杂版面、表格、图表 | 成本和部署复杂度高 |

## 不同文件怎么处理

| 输入类型 | 推荐处理 | 关键 metadata |
| --- | --- | --- |
| 可复制文本 PDF | 直接抽文本，按标题/页码切块 | `page`、`section`、`source` |
| 扫描 PDF | 每页转图片，再 OCR | `page`、`region`、`confidence` |
| 发票/表单图片 | OCR + 字段结构化 | `field_name`、`region`、`confidence` |
| 产品截图 | 视觉 caption + OCR 屏幕文字 | `image_ref`、`ui_area`、`detected_error_code` |
| 图表 | caption + 数据表抽取 | `chart_type`、`axis`、`unit`、`page` |
| 混合文档 | 文本、表格、图片分开生成 evidence | `modality`、`parent_doc_id`、`page` |

## 推荐落库结构

无论用哪种方案，每条证据至少保留：

```json
{
  "chunk_id": "invoice-2026-001:page-1:ocr",
  "source": "invoice-2026-001.pdf",
  "modality": "ocr_text",
  "page": 1,
  "region": "x=80,y=120,w=600,h=180",
  "text": "发票金额 1280 元，购买方：云雀科技",
  "image_ref": "s3://bucket/invoice-2026-001/page-1.png",
  "confidence": 0.93
}
```

这里的 `page`、`region`、`image_ref` 很重要。用户质疑答案时，系统要能定位到原 PDF 页、图片区域和 OCR 结果。

## Evidence 设计原则

一条 evidence 应该能回答三个问题：

```text
它说了什么？
它来自哪里？
用户如何验证？
```

所以不要只保存：

```json
{"text": "发票金额 1280 元"}
```

更好的做法是保存来源和定位信息：

```json
{
  "text": "发票金额 1280 元",
  "source": "invoice-2026-001.pdf",
  "page": 1,
  "region": "x=80,y=120,w=600,h=180",
  "image_ref": "s3://bucket/invoice-2026-001/page-1.png",
  "confidence": 0.93
}
```

这样答案里可以引用“第 1 页发票金额区域”，而不是只说“根据知识库”。

## 处理流程

```text
文件上传
  ↓
判断类型：文本 PDF / 扫描 PDF / 图片 / 混合文档
  ↓
文本抽取 / OCR / 视觉 caption / 表格结构化
  ↓
生成统一 evidence 记录
  ↓
文本索引 + 图片索引 + metadata
  ↓
查询时按问题类型选择检索器或混合召回
  ↓
返回文本证据，并附原图/PDF 页引用
```

## 图文检索的两种查询

**文本查图片**

用户输入文字：

```text
截图里的 E1024 是什么问题？
```

系统需要命中图片 caption 或 OCR：

```text
产品上传页面弹出错误码 E1024，提示文件超过大小限制。
```

**图片查文本**

用户上传一张截图，系统先做 OCR/视觉理解：

```text
图片内容：上传页面，错误码 E1024，文件超过大小限制。
```

再用这段结构化描述去检索文本知识库，找到错误码处理文档。

## 实战判断

- 用户问“退款规则是什么”：优先文本 RAG。
- 用户问“发票金额是多少”：OCR 文本和表格结构化更重要。
- 用户问“截图里这个按钮在哪里”：视觉 caption 或图片检索更重要。
- 用户问“这页 PDF 的图表说明什么”：页面级视觉检索或图表 caption 更合适。

## 评估指标

多模态 RAG 除了普通 RAG 指标，还要看解析质量：

| 指标 | 说明 |
| --- | --- |
| OCR 字段准确率 | 金额、日期、证件号、错误码是否识别正确 |
| 页面定位准确率 | 引用的 PDF 页码和区域是否正确 |
| Caption 可用率 | 图片描述是否足以支撑检索和回答 |
| 图表事实准确率 | 数值、趋势、单位是否正确 |
| Evidence 可追溯率 | 答案是否能回到原图或原 PDF 区域 |
| 多模态 Recall@K | 图文证据是否进入 Top-K |

高风险业务里，OCR 金额、合同条款、证件号不能只靠模型输出，应该有规则校验或人工复核。

## 常见错误

- 只保存 OCR 文本，不保存页码和区域。
- 扫描 PDF 当普通 PDF 解析，结果得到空文本。
- 图表只 OCR，丢掉坐标、表头、单位和趋势。
- 图片 caption 太泛，比如“这是一张界面截图”，无法支撑问答。
- 不记录 OCR 置信度，导致低质量识别结果直接进入答案。
- 图文检索没有评估集，只凭演示样例判断效果。

## 运行后观察点

脚本模拟了四类 evidence：

- `pdf_text`：普通 PDF 文本。
- `ocr_text`：扫描 PDF 或图片 OCR。
- `image_caption`：截图的视觉描述。
- `chart_caption`：图表页面的视觉描述。

运行后重点看三个问题：

```text
发票金额是多少
截图里的 E1024 是什么问题
Q2 企业版收入是多少
```

每个问题排第一的 evidence 类型不同，说明查询意图会影响检索器选择和排序策略。

## 练习

给你业务里的 3 类文件各设计一条 evidence：

1. 一页扫描合同。
2. 一张产品报错截图。
3. 一个包含柱状图的 PDF 页面。

要求写出 `chunk_id`、`source`、`modality`、`page`、`region`、`text`、`image_ref` 和 `confidence`。
