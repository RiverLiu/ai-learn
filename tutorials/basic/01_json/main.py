"""JSON 与 Python 对象的互相转换。

JSON（JavaScript Object Notation）是一种纯文本的数据格式，
几乎所有编程语言都认识它，因此成了程序之间交换数据的"普通话"。

Python 标准库 json 提供两组函数：
- dumps / loads：Python 对象 <-> JSON 字符串（s = string）
- dump  / load ：Python 对象 <-> JSON 文件

本章全程离线运行，直接观察每一步的输出即可。
"""

import json
from datetime import datetime
from pathlib import Path

DATA_FILE = Path(__file__).parent / "data.json"
OUTPUT_FILE = Path(__file__).parent / "output.json"  # 本章生成的文件（已 gitignore）


def basics():
    """第一组基本功：dumps 序列化、loads 反序列化。"""
    print("===== 1. dumps / loads =====")

    user = {"name": "小明", "age": 25, "skills": ["Python", "Git"]}

    # dumps：Python 对象 -> JSON 字符串（序列化）
    text = json.dumps(user, ensure_ascii=False)
    print(f"Python 对象：{user}")
    print(f"JSON 字符串：{text}")
    print(f"类型变化：{type(user)} -> {type(text)}")

    # loads：JSON 字符串 -> Python 对象（反序列化）
    parsed = json.loads(text)
    print(f"解析回来：{parsed}，name 字段 = {parsed['name']}")

    # 注意：ensure_ascii=False 让中文原样输出；
    # 不加它中文会被转义成 \u5c0f\u660e 这种形式（仍然合法，只是人看着累）
    print(f"不加 ensure_ascii=False：{json.dumps(user)}")


def type_mapping():
    """JSON 类型与 Python 类型的对应关系（重点记忆）。"""
    print("\n===== 2. 类型对应表 =====")
    examples = {
        "对象 object  -> dict": '{"a": 1}',
        "数组 array   -> list": "[1, 2, 3]",
        "字符串 string -> str": '"hello"',
        "数字 number  -> int/float": "42",
        "true         -> True": "true",
        "false        -> False": "false",
        "null         -> None": "null",
    }
    for desc, json_text in examples.items():
        value = json.loads(json_text)
        print(f"  {desc:28s} 解析结果：{value!r}（{type(value).__name__}）")


def dumps_options():
    """dumps 的三个常用参数。"""
    print("\n===== 3. 美化输出：indent 与 sort_keys =====")
    data = {"b": 2, "a": 1, "c": [3, 1]}
    # indent=2：格式化缩进，适合给人看；sort_keys=True：键按字母排序
    print(json.dumps(data, ensure_ascii=False, indent=2, sort_keys=True))


def file_io():
    """dump / load：JSON 与文件的互相转换。"""
    print("\n===== 4. 文件读写：dump / load =====")

    # 读取本章附带的 data.json（注意 open 时指定 encoding="utf-8"）
    with open(DATA_FILE, encoding="utf-8") as f:
        profile = json.load(f)
    print(f"从 {DATA_FILE.name} 读到：{profile['name']}，技能 {profile['skills']}")

    # 修改后写入新文件（dump 的参数与 dumps 相同）
    profile["age"] += 1
    profile["skills"].append("asyncio")
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(profile, f, ensure_ascii=False, indent=2)
    print(f"已写入 {OUTPUT_FILE.name}（age+1、新增技能）")


def common_pitfalls():
    """初学者最常撞见的三个坑。"""
    print("\n===== 5. 常见坑 =====")

    # 坑 1：JSON 文本不是 Python 字面量——单引号、True、None 都是非法 JSON
    try:
        json.loads("{'name': '小明'}")  # 单引号！非法
    except json.JSONDecodeError as e:
        print(f"  坑1 单引号不是合法 JSON：{type(e).__name__}: {e}")

    # 坑 2：不是所有 Python 对象都能序列化（datetime、set、自定义类…）
    try:
        json.dumps({"time": datetime.now()})
    except TypeError as e:
        print(f"  坑2 datetime 不能直接序列化：{e}")
    # 解法：用 default 参数告诉 json 遇到不认识的对象怎么办
    text = json.dumps({"time": datetime(2026, 7, 19, 12, 0)}, default=str, ensure_ascii=False)
    print(f"      default=str 之后：{text}")

    # 坑 3：转换不是完全可逆的——tuple 会变成 list
    original = {"point": (1, 2)}
    restored = json.loads(json.dumps(original))
    print(f"  坑3 元组变列表：{original['point']!r} -> {restored['point']!r}")


def main():
    basics()
    type_mapping()
    dumps_options()
    file_io()
    common_pitfalls()


if __name__ == "__main__":
    main()
