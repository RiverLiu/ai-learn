# 02 Agent 轨迹

Agent 的最终答案正确，不代表过程安全。生产系统要记录它每一步做了什么。

## 轨迹示例

```json
[
  {"step": 1, "type": "thought", "summary": "需要先检索退款规则"},
  {"step": 2, "type": "tool_call", "name": "search_docs", "args": {"query": "退款规则"}},
  {"step": 3, "type": "tool_result", "name": "search_docs", "status": "ok"},
  {"step": 4, "type": "final_answer"}
]
```

## 必须记录

- step 编号
- 工具名称
- 参数摘要
- 权限校验结果
- 耗时
- 错误信息
- 停止原因

## 练习

为 `tutorials/10_langgraph/03_react_agent` 增加一个轨迹结构设计，说明如何限制最大工具调用步数。
