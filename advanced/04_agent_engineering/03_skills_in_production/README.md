# 03 Skills 生产化

Skills 不只是本地提示词文件。团队使用时要考虑版本、触发、验证和维护责任。

## 生产化要点

- Skill 名称稳定。
- `description` 覆盖真实触发场景。
- `SKILL.md` 保持短，长资料放 `references/`。
- 确定性操作放 `scripts/`。
- 每次修改后用样例请求验证触发效果。

## 示例

```text
customer-support-skill/
├── SKILL.md
├── references/
│   ├── refund_policy.md
│   └── escalation_rules.md
└── scripts/
    └── check_ticket_export.py
```

## 练习

把 `tutorials/13_skills/01_anatomy/csv-cleaner` 改造成团队可复用 Skill，补充 5 条 should trigger 和 5 条 should not trigger 样例。
