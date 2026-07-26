"""提示词模板与输出解析：把"字符串拼接"升级为可复用的组件。"""

import os

from dotenv import load_dotenv
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field

load_dotenv()


def get_model() -> ChatOpenAI:
    return ChatOpenAI(model=os.getenv("MODEL_NAME", "gpt-4o-mini"))


def prompt_demo():
    """ChatPromptTemplate：带占位符的消息模板，一处定义处处复用。"""
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", "你是翻译助手，把用户输入翻译成{language}，只输出译文。"),
            ("human", "{text}"),
        ]
    )

    # 不调用模型，先预览渲染后的消息（调试提示词的常用手段）
    rendered = prompt.invoke({"language": "英文", "text": "向量数据库很强大"})
    print("【模板渲染结果】")
    for message in rendered.to_messages():
        print(f"  {message.type}: {message.content}")

    # prompt | model | parser：三个组件用管道符串成一条链（第 3 章详解）
    model = get_model()
    chain = prompt | model | StrOutputParser()  # StrOutputParser：AIMessage -> 纯字符串
    result = chain.invoke({"language": "日文", "text": "向量数据库很强大"})
    print(f"【翻译链】{result}")


def structured_output_demo():
    """with_structured_output：让模型按 Pydantic 模型返回，字段带类型与校验。"""

    class Recipe(BaseModel):
        """一份菜谱。"""

        name: str = Field(description="菜名")
        difficulty: int = Field(description="难度，1 到 5", ge=1, le=5)
        ingredients: list[str] = Field(description="所需食材")

    model = get_model().with_structured_output(Recipe)
    recipe = model.invoke("教我做一道简单的番茄炒蛋")
    print(f"【结构化输出】菜名：{recipe.name}，难度：{recipe.difficulty}")
    print(f"  食材：{recipe.ingredients}")
    print(f"  （拿到的是 {type(recipe).__name__} 对象，不是 JSON 字符串，无需手动解析）")


def main():
    prompt_demo()
    structured_output_demo()


if __name__ == "__main__":
    main()
