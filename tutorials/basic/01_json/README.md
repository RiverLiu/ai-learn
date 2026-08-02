# 01 JSON：程序之间的"普通话"

## JSON 是什么

JSON 是一种**纯文本**的数据格式，用来在程序之间传递结构化的数据。
它长得像 Python 的字典和列表，但它是与语言无关的文本——Python 程序写出来的 JSON，
Java、Go、JavaScript 程序都能读。你之后调任何 HTTP API，请求体和响应体十有八九是 JSON。

## 四个函数，两组场景

| 函数 | 方向 | 场景 |
| --- | --- | --- |
| `json.dumps(obj)` | Python 对象 → JSON **字符串** | 要发给 API、存进数据库字段 |
| `json.loads(text)` | JSON 字符串 → Python **对象** | 收到 API 响应后要取字段 |
| `json.dump(obj, f)` | Python 对象 → JSON **文件** | 保存配置、导出数据 |
| `json.load(f)` | JSON 文件 → Python **对象** | 读取配置、导入数据 |

记忆技巧：带 `s` 的操作**字符串**（string），不带 `s` 的操作**文件**。

## 类型对应表（必须记住）

| JSON | Python | 注意 |
| --- | --- | --- |
| object `{...}` | `dict` | 键必须是字符串 |
| array `[...]` | `list` | tuple 会被转成 list（不可逆） |
| string `"..."` | `str` | JSON 只认**双引号** |
| number | `int` / `float` | |
| `true` / `false` | `True` / `False` | 大小写不同！ |
| `null` | `None` | 写法不同！ |

## 三个最常用的参数

```python
json.dumps(data, ensure_ascii=False, indent=2, sort_keys=True)
```

- `ensure_ascii=False`：中文原样输出。不加的话中文变成 `\u5c0f\u660e` 转义序列
  （数据没错，但人和日志都看不懂）——**处理中文时几乎必加**。
- `indent=2`：美化缩进。给人看的文件（配置、导出）加上；机器之间传输可以不加（省体积）。
- `sort_keys=True`：键按字母排序，输出稳定，方便 diff 对比。

读文件时养成习惯：`open(path, encoding="utf-8")`，显式指定编码，避免中文乱码。

## 初学者最常撞的坑（代码第 5 节有现场演示）

1. **把 Python 字面量当 JSON 解析**：`{'a': 1}`（单引号）、`True`、`None` 都不是合法 JSON，
   会抛 `json.JSONDecodeError`。JSON 只认双引号、`true/false/null`。
2. **不是所有对象都能序列化**：`datetime`、`set`、自定义类实例会抛 `TypeError`。
   用 `default` 参数兜底：`json.dumps(obj, default=str)`。
3. **转换不完全可逆**：`tuple` 序列化再解析回来变成 `list`；字典的整数键会变成字符串键。
   对数据类型敏感的场景，解析后要自己转回来。

## 运行

```bash
uv run tutorials/basic/01_json/main.py
```

`data.json` 是本章的示例输入；运行会生成 `output.json`（已 gitignore，可随意删除）。

## 练习建议

1. 给 `data.json` 加一个 `"hobbies"` 字段，重新运行，观察输出。
2. 写一个函数：读取 `output.json`，把 `"skills"` 去重后写回去。
3. 故意把 `data.json` 的某个双引号改成单引号，运行第 4 节，看报错的行号提示。
