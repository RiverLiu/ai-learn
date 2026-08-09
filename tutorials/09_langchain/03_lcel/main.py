"""LCEL（LangChain Expression Language）：用 | 把组件组合成链。

LCEL 的核心思想：模型、提示词、解析器、普通函数都是 Runnable（可运行组件），
用管道符 | 连接后得到的新组件依然是 Runnable，统一支持 invoke/stream/batch。
"""

import os

from dotenv import load_dotenv
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableLambda, RunnableParallel
from langchain_openai import ChatOpenAI

load_dotenv()


def get_model() -> ChatOpenAI:
    return ChatOpenAI(model=os.getenv("MODEL_NAME", "gpt-4o-mini"))


def basic_chain():
    """最基础的链：提示词 -> 模型 -> 字符串。"""
    prompt = ChatPromptTemplate.from_template("用一句话向{audience}解释{topic}")
    chain = prompt | get_model() | StrOutputParser()

    # 整条链同样支持 invoke / stream / batch
    print("【基础链】", chain.invoke({"audience": "小学生", "topic": "区块链"}))


def two_stage_chain():
    """链可以接链：第一级生成内容，第二级加工。"""
    writer = ChatPromptTemplate.from_template("写一句关于{topic}的宣传语") | get_model() | StrOutputParser()
    reviewer = (
        ChatPromptTemplate.from_template("给这句宣传语起一个 4 字以内的中文标题：\n{slogan}")
        | get_model()
        | StrOutputParser()
    )
    # 用 dict 把第一级的输出包装成第二级需要的变量名
    chain = writer | (lambda slogan: {"slogan": slogan}) | reviewer
    print("【两级链】标题：", chain.invoke({"topic": "云雀笔记"}))


def custom_and_parallel():
    """RunnableLambda 把普通函数变成链组件；RunnableParallel 并行执行多条链。"""
    model = get_model()

    def word_count(text: str) -> str:
        return f"（共 {len(text)} 字）"

    chain = (
        ChatPromptTemplate.from_template("介绍一下{city}")
        | model
        | StrOutputParser()
        | RunnableParallel(  # 同一个字符串输入，并行喂给两个分支
            {
                "content": RunnableLambda(lambda x: x),  # 原样透传
                "stats": RunnableLambda(word_count),      # 本地统计
            }
        )
    )
    result = chain.invoke({"city": "杭州"})
    print(f"【并行分支】统计：{result['stats']}")
    print(f"  内容：{result['content'][:60]}...")


def main():
    basic_chain()
    two_stage_chain()
    custom_and_parallel()


if __name__ == "__main__":
    main()
