"""用 LangChain 重写 RAG：对比 rag 教程的手写版本，体会框架带来的变化。

流水线与 tutorials/07_rag 完全相同：加载 -> 切块 -> 向量化 -> 检索 -> 拼提示词 -> 生成。
区别在于每一步都换成了 LangChain 组件，整条链用 LCEL 组装。

运行：uv run tutorials/09_langchain/04_rag/main.py "你的问题"
"""

import os
import sys
from pathlib import Path

from dotenv import load_dotenv
from langchain_core.documents import Document
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.vectorstores import InMemoryVectorStore
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_text_splitters import MarkdownHeaderTextSplitter, RecursiveCharacterTextSplitter

load_dotenv()

KB_DIR = Path(__file__).parent / "knowledge_base"


def load_markdown_docs(kb_dir: Path) -> list[Document]:
    """读取知识库中的 Markdown 文件为 Document 列表。

    Document = page_content（正文）+ metadata（元数据，如来源文件名）。
    生产中可改用 langchain-community 的 DirectoryLoader 支持更多格式。
    """
    return [
        Document(page_content=path.read_text(encoding="utf-8"), metadata={"source": path.name})
        for path in sorted(kb_dir.glob("*.md"))
    ]


def build_retriever():
    """离线索引：加载 Markdown -> 按标题切块 -> 向量化 -> 内存向量库。"""
    docs = load_markdown_docs(KB_DIR)
    print(f"加载了 {len(docs)} 篇文档")

    # 先按 Markdown 标题切成大块，超长块再按字符细分（rag 教程第 2 章的框架版）
    header_splitter = MarkdownHeaderTextSplitter(headers_to_split_on=[("#", "标题"), ("##", "小节")])
    char_splitter = RecursiveCharacterTextSplitter(chunk_size=300, chunk_overlap=30)
    header_chunks = []
    for doc in docs:
        for chunk in header_splitter.split_text(doc.page_content):
            # 标题切块器生成的新 Document 不带原文档 metadata，手动把来源传下去
            chunk.metadata["source"] = doc.metadata["source"]
            header_chunks.append(chunk)
    chunks = char_splitter.split_documents(header_chunks)
    print(f"切出 {len(chunks)} 个块")

    embeddings = OpenAIEmbeddings(model=os.getenv("EMBEDDING_MODEL", "text-embedding-3-small"))
    vectorstore = InMemoryVectorStore.from_documents(chunks, embeddings)
    return vectorstore.as_retriever(search_kwargs={"k": 3})


def format_docs(docs: list[Document]) -> str:
    """把检索到的 Document 列表拼成提示词中的上下文文本，并标注来源。"""
    return "\n\n".join(
        f"【资料{i + 1}】（来源：{Path(doc.metadata.get('source', '未知')).name}）\n{doc.page_content}"
        for i, doc in enumerate(docs)
    )


def main():
    question = " ".join(sys.argv[1:]) or "专业版多少钱？学生有优惠吗？"

    retriever = build_retriever()
    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                "你是知识库问答助手。只根据给定资料回答，资料中没有就明说不知道，"
                "回答结尾用【来源：xxx】注明依据。",
            ),
            ("human", "资料：\n{context}\n\n问题：{question}"),
        ]
    )
    model = ChatOpenAI(model=os.getenv("MODEL_NAME", "gpt-4o-mini"))

    # RAG 链：question 一路原样传递，另一路经检索器变成 context
    chain = (
        {"context": retriever | format_docs, "question": RunnablePassthrough()}
        | prompt
        | model
        | StrOutputParser()
    )

    print(f"\n问题：{question}")
    print(f"回答：{chain.invoke(question)}")


if __name__ == "__main__":
    main()
