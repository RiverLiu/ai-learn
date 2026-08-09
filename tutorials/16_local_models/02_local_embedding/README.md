# 02 本地向量模型：Embedding 也能离线跑

上一章让聊天模型本地化，这一章把 **Embedding（文本向量）** 也搬到本地——
RAG 教程里建索引、做检索都要反复调 Embedding 接口，本地化之后整条 RAG 流水线彻底离线、免费。
本章用国产开源的 **bge-m3**（智源研究院 BAAI 出品，多语言、中文效果好）复现
[RAG 第 1 章](../../07_rag/01_embeddings/) 的语义相似度演示。

## 本章要点

- Embedding 本地化三理由：**隐私**（知识库文档不发给第三方）、**免费**（建索引动辄成千上万次调用）、**离线**（无网环境也能建库检索）。
- **方案一（本章演示）**：`ollama pull bge-m3` 后，Ollama 的 OpenAI 兼容端点同样提供 `/v1/embeddings`，
  代码只需换 `base_url` 和模型名，与聊天模型共用一套配置。
- **方案二**：`sentence-transformers` 库直接在 Python 进程里加载模型（需额外安装，本项目未内置），适合不想跑 Ollama 服务的场景。
- **换 Embedding 模型必须重建索引**：不同模型向量维度不同（bge-m3 是 1024 维，OpenAI text-embedding-3-small 是 1536 维），
  语义空间也不同，旧索引里的向量在新模型下没有意义——RAG 第 3 章的 `rag_index.npz` 要删掉重建。

## 运行

```bash
uv run tutorials/16_local_models/02_local_embedding/main.py
```

脚本是"检测-引导"模式：

- 检测到 Ollama 在线且已拉取 `bge-m3`：对 1 个查询 + 3 个候选句生成向量，按余弦相似度排序输出；
- 未检测到：打印安装与配置指引并正常退出（退出码 0）。

预期效果与 RAG 第 1 章一致：两条"价格"相关的句子排前，无关的 React 条目垫底——
只是这次向量全程由本机的 bge-m3 产生，没有发出任何网络请求。

## 核心概念

### 为什么 Embedding 也值得本地化

聊天机器人一次对话调几次模型就完了；而 RAG **建索引**时要给知识库的每个文本块都算一次向量，
库一大就是成千上万次调用——用付费 API 既花钱又把私有文档内容发了出去。
Embedding 模型本身很小（bge-m3 仅约 0.5B 参数，普通电脑跑得飞快），是本地化性价比最高的一环。

### 方案一：Ollama + bge-m3（OpenAI 兼容）

```bash
ollama pull bge-m3     # 约 1 GB 出头，具体大小以官网模型库为准
```

调用方式与聊天完全同一套（`base_url=http://localhost:11434/v1`，`api_key="ollama"`），
只是换成 `client.embeddings.create(model="bge-m3", ...)`——本章 `main.py` 有完整演示。

接回 RAG 教程：在项目根目录 `.env` 追加一行即可（聊天配置沿用第 1 章）：

```bash
EMBEDDING_MODEL=bge-m3
```

然后删掉旧索引重建（换模型后维度、语义空间都变了）：

```bash
rm -f tutorials/07_rag/03_vector_store/rag_index.npz tutorials/07_rag/03_vector_store/rag_index.json
uv run tutorials/07_rag/03_vector_store/main.py   # 用 bge-m3 重建索引
```

### 方案二：sentence-transformers 库直跑

不想常驻 Ollama 服务时，可以用 [sentence-transformers](https://sbert.net/) 在 Python 进程内直接加载模型
（**需自行额外安装，本项目未内置**：`uv add sentence-transformers`，首次运行会从 Hugging Face 下载权重）：

```python
from sentence_transformers import SentenceTransformer

model = SentenceTransformer("BAAI/bge-m3")
vectors = model.encode(["第一句", "第二句"])   # 返回 numpy 数组，可直接做余弦相似度
```

国内下载 Hugging Face 权重较慢时，可设置镜像环境变量 `HF_ENDPOINT=https://hf-mirror.com` 后再运行。
注意它返回的是原生 numpy 向量，不是 OpenAI 响应格式，接入 RAG 教程需要改少量调用代码。

### 两个方案怎么选

| | Ollama + bge-m3 | sentence-transformers |
| --- | --- | --- |
| 与 RAG 教程的衔接 | **零改动**（改 `.env` 即可） | 需改写向量获取代码 |
| 运行方式 | 独立服务，多语言都能调 | Python 进程内，随用随起 |
| 额外依赖 | 无（沿用 openai SDK） | 需安装 sentence-transformers 及 PyTorch |

## 常见错误

1. **`ollama run bge-m3` 报 `does not support generate`**：bge-m3 是纯向量模型，不能对话，
   只能通过 Embedding 接口取向量——这不是故障，用法见本章 main.py。
2. **`model 'bge-m3' not found`**：先 `ollama pull bge-m3`，用 `ollama list` 确认。
3. **换了 Embedding 模型没重建索引**：轻则检索质量莫名暴跌（两个模型的语义空间对不上），
   重则维度不匹配直接报错（1024 维 vs 1536 维）。**换模型 = 删旧索引 + 重建**。
4. **期望向量维度和旧索引一致**：在 `.env` 里混用不同家的 `EMBEDDING_MODEL` 时，
   先确认各自维度，RAG 第 3 章存索引时维度就已固定。

## 练习建议

1. 把本章 main.py 的候选句换成你自己知识库里的真实句子，看 bge-m3 的语义排序是否符合直觉。
2. 完成 `.env` 配置并重建索引后，运行 `uv run tutorials/07_rag/04_rag_pipeline/main.py`，
   体验"聊天 + 向量全本地"的完整 RAG。
3. 有余力可安装 sentence-transformers，用它重写本章演示，对比两种方案的代码差异与启动开销。
