# 05 结合 LLM 构建迷你 Agent

这是本教程的收官章节：把 MCP 工具接入 LLM 的 function calling 流程，
实现一个最小的 Agent——用户用自然语言提问，LLM 自己决定调用哪些 MCP 工具并汇总答案。

## 本章要点

- MCP 工具的参数本身就是 JSON Schema，可以**直接**转换为 OpenAI tools 格式，无需手写函数声明。
- Agent 主循环：
  1. 把对话历史 + 工具列表发给 LLM；
  2. 若 LLM 返回 `tool_calls`，通过 MCP Client 逐个执行，把结果追加到对话；
  3. 重复，直到 LLM 返回纯文本回答。
- 这个循环就是 Claude Desktop 等宿主应用的核心工作方式，本章是它的极简复刻。

## 运行

需要 `OPENAI_API_KEY`；使用兼容 OpenAI 协议的服务时，还需 `OPENAI_BASE_URL` 和 `MODEL_NAME`。
两种配置方式任选其一：

方式一：`.env` 文件——复制本章的 `.env.example` 为 `.env` 并填入真实配置即可
（脚本会优先加载本章目录的 `.env`，其次向上查找到项目根目录的 `.env`）：

```bash
cp tutorials/mcp/05_llm_agent/.env.example tutorials/mcp/05_llm_agent/.env
# 编辑 .env 填入密钥后运行
uv run tutorials/mcp/05_llm_agent/agent.py "北京天气怎么样？顺便算算 10 除以 4"
```

方式二：环境变量（优先级高于 .env，不会被覆盖）：

```bash
export OPENAI_API_KEY="sk-..."
uv run tutorials/mcp/05_llm_agent/agent.py "北京天气怎么样？顺便算算 10 除以 4"
```

预期输出（具体文字因模型而异）：

```
调用工具 get_weather，参数 {'city': '北京'}
调用工具 divide，参数 {'a': 10, 'b': 4}
最终回答：北京今天晴，气温 32°C。10 除以 4 等于 2.5。
```

## 核心概念

- **MCP + function calling 是互补关系**：function calling 定义"模型如何表达调用意图"，
  MCP 定义"工具如何被发现和执行"，二者通过 JSON Schema 无缝衔接。
- **工具描述影响调度质量**：LLM 只能看到工具名、docstring 和参数 Schema，
  写得越清楚，模型选工具、填参数越准确——回到第 2 章重新审视一下那些 docstring。
