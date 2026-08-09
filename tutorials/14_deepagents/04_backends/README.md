# 04 文件系统后端：文件写到哪里

Agent 的"文件系统"是个抽象层，写到哪里由 `backend` 参数决定：

| 后端 | 文件存放在 | 生命周期 | 适用 |
| --- | --- | --- | --- |
| `StateBackend`（默认） | 图的状态字段 `files` | 随会话（thread）存亡 | 中间草稿、一次性任务 |
| `FilesystemBackend(root_dir=...)` | 真实磁盘目录 | 永久（除非删除） | Agent 交付物、代码工程 |
| `StoreBackend()` | LangGraph Store（需配 `store=`） | 跨会话持久 | 用户档案、长期笔记（呼应 [memory 教程](../../11_memory/)） |

## 本章要点

- **换后端不改行为**：`write_file`/`read_file` 的用法对 Agent 完全一样，
  只是落点不同——抽象的代价为零。
- `FilesystemBackend` 让 Agent 的产出直接成为工作目录里的文件：本章运行后
  可以在 `workspace/` 里亲眼看到 `pricing_note.md`。
  **务必传 `virtual_mode=True`**：否则（默认 `False`）绝对路径会**绕过** `root_dir`
  直接写到真实文件系统的对应位置，既是 bug 温床也是安全隐患；`virtual_mode=True`
  把 `/pricing_note.md` 映射进 `root_dir` 内并阻止 `..` 逃逸。
- `StoreBackend` 与 `create_deep_agent(store=...)` 搭配：两个互不认识的 Agent 实例
  通过同一个 Store 读写同一份文件——这就是跨会话持久化（内存版 Store 仅用于演示）。
  记得显式传 `namespace`（如按 user_id 生成），0.7 起将成为必需。
- 还有 `CompositeBackend`（按路径前缀路由到不同后端，如 `/memories/` 进 Store、
  其余进磁盘）和 `LocalShellBackend`（真实 shell 执行），按需查阅官方文档。

## 运行

```bash
uv run tutorials/14_deepagents/04_backends/main.py
```

## 核心概念

- **选型即架构**：State 后端适合"用完即弃的工作台"，Filesystem 适合"交付物"，
  Store 适合"记住用户"。一个系统里三者可以共存（CompositeBackend）。
- `workspace/` 目录已加入 gitignore；Store 持久化选型见
  [langgraph 教程第 5 章](../../10_langgraph/05_persistence/)。
