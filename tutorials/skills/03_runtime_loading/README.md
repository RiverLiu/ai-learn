# 03 运行时加载示例

本章用一个小 Python 程序模拟 Skills 的核心流程：

1. 扫描技能目录。
2. 读取每个 `SKILL.md` 的 frontmatter。
3. 根据用户请求匹配最相关的 Skill。
4. 只在命中后加载正文。

这不是完整的 Codex 实现，只是帮助理解 Skills 的工程思想：**元数据先行，正文按需加载，资源继续延迟读取**。

## 运行

```bash
uv run tutorials/skills/03_runtime_loading/main.py
```

预期输出会展示三个请求分别匹配到不同 Skill，并打印被加载的正文片段。

## 示例目录

```text
03_runtime_loading/
├── main.py
└── sample_skills/
    ├── csv-cleaner/
    │   └── SKILL.md
    ├── fastapi-review/
    │   └── SKILL.md
    └── product-report/
        └── SKILL.md
```

## 核心概念

### 只扫描 frontmatter

真正的 Skills 系统不会一开始把所有 Skill 正文都塞进上下文。它先看轻量元数据：

```yaml
name: csv-cleaner
description: Clean, validate, normalize, and summarize CSV files...
```

这一步成本很低，可以同时比较多个 Skill。

### 命中后再读正文

当用户请求类似 “帮我清理销售 CSV” 时，系统才读取 `csv-cleaner/SKILL.md` 正文，拿到具体步骤。

这就是渐进披露：

```text
用户请求
  ↓
候选 Skill 元数据
  ↓
命中的 SKILL.md 正文
  ↓
必要时再读 references/scripts/assets
```

### 示例匹配算法很简单

本章代码使用词项重叠做演示。生产系统通常会用更可靠的检索、排序、规则或模型判断。
重点不是算法本身，而是加载边界：

- 匹配阶段只需要 `name` 和 `description`。
- 执行阶段才加载正文。
- 详细资料继续按需读取。

## 与真实 Agent 的差异

真实 Agent 还会处理：

- 多个 Skill 同时触发。
- Skill 优先级和冲突。
- 用户明确点名 Skill。
- 资源文件分页读取。
- 工具权限和沙箱。
- 脚本执行前后的验证。

本章只保留最小路径，便于理解。
