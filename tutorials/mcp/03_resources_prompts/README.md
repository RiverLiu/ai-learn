# 03 Resources 与 Prompts

除了 Tools，MCP Server 还可以暴露另外两种原语：**Resources**（可读取的数据）和 **Prompts**（提示词模板）。

## 本章要点

- **Resource**：用 URI 标识的一份数据，由应用/用户主动读取（类似 GET 请求），通常作为上下文注入对话。
  - 静态 Resource：`@mcp.resource("config://app")`，URI 固定。
  - Resource 模板：`@mcp.resource("user://{user_id}/profile")`，URI 中的占位符会映射为函数参数。
- **Prompt**：`@mcp.prompt()` 把函数注册的返回值作为提示词模板，用户可以在宿主应用中一键选用，免去重复编写。

## 运行

```bash
cd tutorials/mcp/03_resources_prompts
uv run mcp dev server.py
```

在 Inspector 中试试：

- **Resources** 标签页：读取 `config://app`；在模板 `user://{user_id}/profile` 中填入 `001` 读取小明的资料。
- **Prompts** 标签页：选择 `translate_to_english`，填入一段中文，查看生成的提示词。

## 核心概念

- **Tools vs Resources**：Tool 是"做事"（可能有副作用），Resource 是"读数据"（只读、幂等）。
  查天气、发消息用 Tool；读配置、读文件用 Resource。
- **三种原语的分工**：Tools 由模型决定调用，Resources 由应用选择加载，Prompts 由用户主动触发。
