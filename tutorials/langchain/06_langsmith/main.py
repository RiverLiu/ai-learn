"""LangSmith 追踪：不改业务代码，用环境变量开启全链路观测。

开启后，每次链/模型/工具调用的输入输出、耗时、token 用量都会自动上传到
LangSmith 平台（https://smith.langchain.com），形成可视化的调用链（trace）。

本脚本演示：开了追踪就跑一条链；没开则打印配置指引。
"""

import os

from dotenv import load_dotenv

load_dotenv()  # LANGSMITH_* 变量从 .env 或环境读取（参考 .env.example）

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI


def main():
    if os.getenv("LANGSMITH_TRACING", "").lower() != "true":
        print("未开启 LangSmith 追踪。配置方式（写入 .env 或 export）：")
        print("  LANGSMITH_TRACING=true")
        print("  LANGSMITH_API_KEY=ls__...   # 在 https://smith.langchain.com 创建")
        print("  LANGSMITH_PROJECT=ai-guide  # 可选，默认 default")
        return

    # 与平时完全相同的链——追踪是"免费"的，不需要埋点代码
    chain = (
        ChatPromptTemplate.from_template("用一句话向初学者介绍{topic}")
        | ChatOpenAI(model=os.getenv("MODEL_NAME", "gpt-4o-mini"))
        | StrOutputParser()
    )
    print("回答：", chain.invoke({"topic": "LangSmith"}))
    project = os.getenv("LANGSMITH_PROJECT", "default")
    print(f"\n到 https://smith.langchain.com 的「{project}」项目查看刚才这次运行的完整 trace")


if __name__ == "__main__":
    main()
