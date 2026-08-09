# 02 解剖内建能力

Deep Agent 的"深度"来自三样框架注入的东西，本章让 Agent 把每样都用一遍并留下证据。

## 三味药

- **显式规划（`write_todos`）**：Agent 把任务拆解为 todo 清单写进**状态**（不是聊天记录），
  执行中持续更新 `pending → in_progress → completed`。清单在状态里意味着
  它永远不会被挤出上下文——Agent 随时"看得到"自己做到哪了。
- **上下文卸载（`write_file` / `read_file` / `edit_file` / `ls`）**：
  长文档、中间结果写入虚拟文件系统，上下文里只留路径；需要时 `read_file` 读回。
  这把"上下文窗口"从唯一存储降级为工作内存——长任务的命脉。
- **详尽的内建提示词**：框架在 `system_prompt` 之外叠加了一大段提示词，
  教模型何时规划、何时写文件、何时派子代理。你自己写的 system_prompt 只需
  补充"业务作风"（本章：写完必须读回检查）。

（第四样——子代理——单独留给第 3 章。）

## 运行

```bash
uv run tutorials/14_deepagents/02_builtin_capabilities/main.py
```

预期输出：过程中出现 `write_todos`、`write_file`、`read_file`、`edit_file` 等
**你没有提供的工具名**；结尾打印 todos 清单、`/report.md` 内容和去重后的工具名集合。

## 核心概念

- **状态 vs 消息**：todos 和 files 存在图的状态字段里（`result["todos"]`、`result["files"]`），
  与 `messages` 平级。消息会被截断遗忘，状态字段不会——这是它们能"撑住"长任务的原因。
- 这些能力由 **middleware**（`TodoListMiddleware`、`FilesystemMiddleware` 等）注入，
  `create_deep_agent(middleware=[...])` 可增删——框架不是黑盒，而是一组可拆装的零件。
