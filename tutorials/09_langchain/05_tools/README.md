# 05 工具调用（Tool Calling）

让模型不再局限于文本生成：它可以在回答过程中"申请"调用你提供的函数，拿到结果后再继续。

## 本章要点

- `@tool`：docstring + 类型注解自动生成工具 Schema（与 MCP 教程里 FastMCP 的思路完全一致）。
- `model.bind_tools(tools)`：生成一个"带工具的新模型"，每次请求都附上工具清单。
- **工具调用循环**：
  1. `invoke` 返回的 `AIMessage` 若含 `tool_calls`（名称 + 参数），说明模型想调工具；
  2. 本地执行后把结果包成 `ToolMessage`（带上 `tool_call_id` 对应关系）追加到消息列表；
  3. 再次 `invoke`，直到返回不含 `tool_calls` 的最终回答。

## 运行

```bash
uv run tutorials/09_langchain/05_tools/main.py
```

预期输出：先打印两次"调用工具 ..."日志，再给出汇总了天气和计算结果的回答。

## 核心概念

- **模型只"提议"，不"执行"**：函数永远在你的进程里跑，安全边界由你控制
  （该做权限确认的地方要拦，见 [langgraph 教程第 4 章](../../10_langgraph/04_human_in_loop/)）。
- **手写循环是为了讲清原理**：生产中这个循环由 LangGraph 的 `create_react_agent` 托管，
  一行搞定，还附带状态管理与中断恢复——这正是 [LangGraph 教程](../../10_langgraph/)的内容。
