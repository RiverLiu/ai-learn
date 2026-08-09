# 02 工具进阶

在上一章基础上，演示编写 MCP 工具的几个实用技巧。

## 本章要点

- **异步工具**：`async def` 定义的工具适合网络请求、数据库访问等 I/O 场景，FastMCP 会直接调度到事件循环。
- **结构化输出**：返回 Pydantic 模型（或 dict、list）时，SDK 会生成输出 Schema，
  Client 既能拿到文本内容，也能拿到带类型的结构化数据（`structuredContent`）。
- **错误处理**：工具内直接抛异常即可（如 `ValueError`），SDK 会把它转换为协议错误返回给 Client，
  LLM 能看到错误信息并据此调整后续行为（例如换个参数重试）。
- **参数细节**：支持默认值参数；docstring 与 `Field(description=...)` 会进入工具 Schema，直接影响 LLM 的调用质量。

## 运行

```bash
cd tutorials/12_mcp/02_tools
uv run mcp dev server.py
```

在 Inspector 中试试：

- 调用 `get_weather`，city 填 `北京` → 返回结构化天气数据；填 `火星` → 返回错误。
- 调用 `divide`，b 填 `0` → 返回错误 "除数不能为 0"。
- 调用 `search_files`，keyword 填 `md` → 返回匹配的文件名列表。

## 核心概念

- **输入 Schema**：由函数签名（类型注解 + 默认值）自动生成，约束 LLM 传参。
- **输出 Schema**：由返回值类型生成，让 Client 可以程序化地消费结果。
- **错误即结果**：工具失败不要静默吞掉，抛出异常让 LLM 感知失败原因，是工具设计的基本实践。
