"""文件系统后端：Agent 的"文件"写到哪里，由 backend 决定。

三种后端：
- StateBackend（默认）：文件存在图状态里，随会话存亡；
- FilesystemBackend：写到真实磁盘（Agent 的产出就是工作目录里的文件）；
- StoreBackend：写到 LangGraph Store，跨会话、跨"进程重启"仍在（呼应 memory 教程）。

需要配置模型（见教程首页）。
"""

import os
from pathlib import Path

from dotenv import load_dotenv
from langchain_core.messages import HumanMessage
from langchain_openai import ChatOpenAI
from langgraph.store.memory import InMemoryStore

from deepagents import create_deep_agent
from deepagents.backends import FilesystemBackend, StoreBackend

load_dotenv()

WORKSPACE = Path(__file__).parent / "workspace"  # FilesystemBackend 的工作目录（已 gitignore）

model = ChatOpenAI(model=os.getenv("MODEL_NAME", "gpt-4o-mini"))


def demo_filesystem():
    """真实磁盘后端：Agent 写完，我们直接在工作目录里看到文件。"""
    print("===== 1. FilesystemBackend：写入真实磁盘 =====")
    agent = create_deep_agent(
        model=model,
        tools=[],
        system_prompt="你是写作助手，按用户要求把内容写入指定文件。",
        # virtual_mode=True：把绝对路径也限制在 root_dir 内（防逃逸；默认 False 时绝对路径会绕过 root_dir）
        backend=FilesystemBackend(root_dir=WORKSPACE, virtual_mode=True),
    )
    agent.invoke({"messages": [HumanMessage(content="把『云雀笔记专业版每月 18 元』写入 /pricing_note.md")]})

    real_file = WORKSPACE / "pricing_note.md"
    print(f"磁盘上的文件 {real_file} 存在：{real_file.exists()}")
    if real_file.exists():
        print(f"内容：{real_file.read_text(encoding='utf-8')[:80]}")


def demo_store():
    """Store 后端：文件写入 LangGraph Store，换一个'新 Agent'仍然读得到。"""
    print("\n===== 2. StoreBackend：跨会话持久化 =====")
    store = InMemoryStore()  # 生产换 PostgresStore 等持久化实现

    agent1 = create_deep_agent(
        model=model,
        tools=[],
        system_prompt="你是写作助手，按用户要求把内容写入指定文件。",
        backend=StoreBackend(namespace=lambda ctx: ("demo-files",)),  # 显式命名空间（0.7 起必需）；生产可按 user_id 隔离
        store=store,
    )
    agent1.invoke({"messages": [HumanMessage(content="把『用户偏好：美式咖啡不加糖』写入 /preferences.md")]})
    print("agent1 已写入 /preferences.md")

    # 模拟"重启"：全新 Agent 实例，共享同一个 store
    agent2 = create_deep_agent(
        model=model,
        tools=[],
        system_prompt="你是写作助手。",
        backend=StoreBackend(namespace=lambda ctx: ("demo-files",)),  # 显式命名空间（0.7 起必需）；生产可按 user_id 隔离
        store=store,
    )
    result = agent2.invoke({"messages": [HumanMessage(content="读一下 /preferences.md，告诉我用户的咖啡偏好")]})
    print(f"agent2（新实例）回答：{result['messages'][-1].content}")


def main():
    demo_filesystem()
    demo_store()


if __name__ == "__main__":
    main()
