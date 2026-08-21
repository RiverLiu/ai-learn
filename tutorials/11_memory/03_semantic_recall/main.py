"""语义召回：记忆多了之后，按当前问题检索相关记忆再注入。

第 2 章把全部记忆注入 system prompt，记忆一多就不可行。
本章把记忆向量化存起来，每轮先检索 Top-K 条相关的再注入——
与 RAG 检索同构，但检索对象是动态生长的"记忆"而非静态文档。
"""

import os

from dotenv import load_dotenv
from langchain_core.documents import Document
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langchain_core.vectorstores import InMemoryVectorStore
from langchain_openai import ChatOpenAI, OpenAIEmbeddings

load_dotenv()

model = ChatOpenAI(model=os.getenv("MODEL_NAME", "gpt-4o-mini"))
embeddings = OpenAIEmbeddings(model=os.getenv("EMBEDDING_MODEL", "text-embedding-3-small"), check_embedding_ctx_length=False)

# 模拟一个积累了 10 条记忆的老用户（内容刻意横跨多个领域）
MEMORIES = [
    "用户在减脂，晚餐要低热量",
    "用户不吃辣",
    "用户是后端工程师，主要写 Python",
    "用户叫小明",
    "用户晚上 10 点后才有空锻炼",
    "用户养了一只叫「年糕」的猫",
    "用户预算有限，买书不超过 300 元",
    "用户最近在学 LangGraph",
    "用户喜欢喝美式咖啡，不加糖",
    "用户住在杭州",
]


def build_memory_store() -> InMemoryVectorStore:
    """把记忆向量化入库（生产中持久化到向量数据库，并带 user_id 隔离）。"""
    return InMemoryVectorStore.from_documents(
        [Document(page_content=text) for text in MEMORIES], embeddings
    )


def main():
    store = build_memory_store()
    print(f"记忆库共 {len(MEMORIES)} 条记忆\n")

    for question in ["推荐今晚的晚餐？", "帮我看看这段 Python 代码怎么优化？", "周末去哪玩？"]:
        # 读取环节：按当前问题召回最相关的 3 条记忆，而不是全量注入
        recalled = store.similarity_search(question, k=3)
        print(f"用户：{question}")
        print(f"  召回记忆：{[doc.page_content for doc in recalled]}")

        messages = [
            SystemMessage(
                content="你是贴心的中文助手。关于这位用户，你记得："
                + "；".join(doc.page_content for doc in recalled)
            ),
            HumanMessage(content=question),
        ]
        print(f"  助手：{model.invoke(messages).content}\n")


if __name__ == "__main__":
    main()
