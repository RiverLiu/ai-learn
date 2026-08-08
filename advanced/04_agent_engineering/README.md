# 04 Agent 工程化

基础教程已经介绍了 LangGraph、MCP、Skills、Deep Agents 和多 Agent 模式。
本模块关注生产里的 Agent：如何让它可控、可观测、可测试、可审批。

## 章节目录

1. [01_tool_permission](./01_tool_permission/)：工具权限、风险分级和执行前校验
2. [02_agent_trace](./02_agent_trace/)：Agent 轨迹、步骤记录、循环限制和失败定位
3. [03_skills_in_production](./03_skills_in_production/)：Skills 在团队工作流中的组织、版本和验证
4. [04_human_approval](./04_human_approval/)：高风险工具调用的人机确认流程

## 学习目标

- 能区分普通工具调用和 Agent 长任务。
- 能为工具设计权限和风险等级。
- 能记录 Agent 每一步做了什么。
- 能设计人工审批流程，而不是让模型直接执行高风险动作。

## 示例场景

用户说：

```text
帮我整理这批客户反馈，生成邮件发给客户成功经理。
```

Agent 可能需要：

1. 读取反馈文件。
2. 归类和总结。
3. 生成邮件草稿。
4. 请求用户确认。
5. 调用邮件工具发送。

其中第 5 步必须经过权限检查和人工确认。
