"""本地模型选型辅助表。

离线运行，输出不同任务需要的模型类型和选型检查项。

运行：
    uv run tutorials/16_local_models/03_model_selection/main.py
"""


TASKS = {
    "客服问答": {
        "chat_model": "qwen3:8b 或更强中文聊天模型",
        "embedding_model": "bge-m3",
        "rerank": "可选；知识库变大后建议增加",
        "notes": "先用 10 条真实中文问题评估引用正确性",
    },
    "本地文档检索": {
        "chat_model": "小模型即可，重点在检索质量",
        "embedding_model": "bge-m3 或中文 embedding 模型",
        "rerank": "建议",
        "notes": "换 embedding 模型必须重建索引",
    },
    "代码助手": {
        "chat_model": "代码能力强的 14B+ 模型更稳",
        "embedding_model": "按代码检索场景选择",
        "rerank": "可选",
        "notes": "重点测试长上下文、补全和结构化修改能力",
    },
}


def main() -> None:
    for task, config in TASKS.items():
        print(f"\n===== {task} =====")
        for key, value in config.items():
            print(f"{key}: {value}")

    print("\n选型检查项：")
    checks = [
        "机器内存/显存是否够",
        "中文任务是否稳定",
        "是否需要 embedding 模型",
        "换 embedding 模型后是否重建索引",
        "是否需要流式输出降低等待感",
        "是否用评估集比较模型质量",
    ]
    for index, item in enumerate(checks, start=1):
        print(f"{index}. {item}")


if __name__ == "__main__":
    main()
