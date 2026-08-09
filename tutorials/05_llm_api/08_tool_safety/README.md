# 08 工具调用安全

工具调用让模型能操作外部世界，也带来了风险。生产系统里，模型只能提出工具调用请求，真正执行前必须由应用侧校验。

## 本章要点

- 模型不应该直接拥有执行权限。
- 工具要做白名单、参数校验、权限校验和风险分级。
- 高风险动作需要人工确认。
- 所有工具调用都应该记录审计日志。

## 风险分级

| 风险 | 示例 | 策略 |
| --- | --- | --- |
| 低 | 查询公开知识库、计算退款金额 | 可直接执行 |
| 中 | 查询用户订单、读取内部工单 | 权限校验 + 审计 |
| 高 | 发邮件、退款、删除文件、改数据库 | 人工确认 + 审计 |

## 执行前检查

模型返回：

```json
{
  "name": "refund_order",
  "arguments": {
    "order_id": "ord_123",
    "amount": 299
  }
}
```

应用侧不要直接执行。先检查：

```python
def validate_tool_call(user, tool_name, args):
    if tool_name not in TOOL_REGISTRY:
        raise ValueError("工具不存在")

    tool = TOOL_REGISTRY[tool_name]
    if user.role not in tool.allowed_roles:
        raise PermissionError("无权调用该工具")

    tool.input_schema.model_validate(args)

    if tool.risk == "high":
        return {"status": "needs_approval", "preview": args}

    return {"status": "allowed"}
```

## 人工确认示例

不要只问：

```text
是否允许调用 refund_order？
```

应该展示具体动作：

```text
Agent 想执行退款：

订单号：ord_123
退款金额：299 元
原因：用户购买后 7 天内申请退款

[确认退款] [取消]
```

## 审计日志

每次工具调用建议记录：

```json
{
  "trace_id": "trace_001",
  "user_id": "user_001",
  "tool_name": "refund_order",
  "arguments_summary": {"order_id": "ord_123", "amount": 299},
  "risk": "high",
  "permission_result": "allowed",
  "approval_user": "manager_001",
  "status": "succeeded"
}
```

## 常见错误

- 只靠 prompt 告诉模型“不要乱调用工具”。
- 工具参数不校验，模型传什么就执行什么。
- 没有最大调用步数，Agent 死循环。
- 高风险工具没有人工确认。
- 没有日志，事后无法追踪。

## 与后续模块的关系

- [LangGraph 人机协作](../../10_langgraph/04_human_in_loop/)：框架级 interrupt。
- [Security](../../17_security/)：提示词注入和纵深防御。
- [advanced/04_agent_engineering](../../../advanced/04_agent_engineering/)：生产级 Agent 权限和轨迹。

## 练习

为下面 4 个工具做风险分级：

1. `search_docs(query)`
2. `get_order(order_id)`
3. `send_email(to, subject, body)`
4. `delete_document(document_id)`

说明哪些需要人工确认，以及确认页面应该展示哪些字段。
