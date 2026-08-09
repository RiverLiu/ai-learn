"""Ollama 本地大模型：用 OpenAI SDK 调用跑在本机上的开源模型。

脚本采用"检测-引导"模式，保证任何时候都能运行：
- 检测到本机 Ollama 服务（http://localhost:11434）在线：通过其 OpenAI 兼容端点
  做一次普通对话 + 一次流式输出（模型默认 qwen3:8b）；
- 未检测到：打印分步安装与配置指引，然后正常退出（退出码 0）。
"""

import sys

import httpx

# Ollama 的 OpenAI 兼容端点；原生接口 /api/tags 用于列出本机已安装模型
OLLAMA_BASE_URL = "http://localhost:11434/v1"
OLLAMA_TAGS_URL = "http://localhost:11434/api/tags"
CHAT_MODEL = "qwen3:8b"  # 本章默认模型，改这里即可换成其他已 pull 的模型


def list_local_models() -> list[str] | None:
    """探测 Ollama 服务：在线返回已安装模型名列表，不在线返回 None（2 秒超时，不抛异常）。"""
    try:
        resp = httpx.get(OLLAMA_TAGS_URL, timeout=2.0)
        resp.raise_for_status()
        return [m["name"] for m in resp.json().get("models", [])]
    except httpx.HTTPError:
        return None


def print_install_guide():
    """本机没有 Ollama 时：打印分步安装与配置指引（随后正常退出）。"""
    print("未检测到本机 Ollama 服务（http://localhost:11434）。按下面步骤装好后重跑本脚本：\n")
    print("【第 1 步】安装 Ollama")
    print("  macOS   : 到 https://ollama.com/download/mac 下载 Ollama.dmg 安装并启动；")
    print("            或用 Homebrew：brew install --cask ollama")
    print("  Linux   : curl -fsSL https://ollama.com/install.sh | sh")
    print("  Windows : 到 https://ollama.com/download/windows 下载 OllamaSetup.exe 安装")
    print("  验证    : ollama --version\n")
    print("【第 2 步】拉取模型（约 5 GB，只需一次）")
    print(f"  ollama pull {CHAT_MODEL}")
    print(f"  想先命令行体验一下：ollama run {CHAT_MODEL}（输入 /bye 退出）\n")
    print("【第 3 步】让整套教程接入本地模型：在项目根目录 .env 中写入")
    print("  OPENAI_BASE_URL=http://localhost:11434/v1")
    print("  OPENAI_API_KEY=ollama")
    print(f"  MODEL_NAME={CHAT_MODEL}")
    print("  模板见根目录 .env.example；各章代码通过 load_dotenv() 自动读取。\n")
    print("配好后 rag / langchain / langgraph / deepagents 教程全部原样可用——")
    print("它们只认这三个环境变量，不区分背后是 OpenAI 还是你本机的开源模型。")


def demo_chat():
    """在线演示：一次普通对话 + 一次流式输出，全部走 OpenAI 兼容端点。"""
    from openai import OpenAI

    # 指向本地 Ollama：api_key 不会被校验，但 SDK 要求非空，约定俗成填 "ollama"
    client = OpenAI(base_url=OLLAMA_BASE_URL, api_key="ollama")

    # —— 普通对话：等模型一次性生成完再拿到完整回答 ——
    question = "用一句话向初学者解释什么是大语言模型。"
    print(f"【普通对话】问：{question}")
    resp = client.chat.completions.create(
        model=CHAT_MODEL,
        messages=[{"role": "user", "content": question}],
    )
    print(f"答：{resp.choices[0].message.content}\n")

    # —— 流式输出：边生成边打印，长回答不用干等（打字机效果）——
    question2 = "列举本地跑开源模型的三个好处。"
    print(f"【流式输出】问：{question2}")
    print("答：", end="", flush=True)
    stream = client.chat.completions.create(
        model=CHAT_MODEL,
        messages=[{"role": "user", "content": question2}],
        stream=True,  # 开启流式：返回的是逐块（chunk）迭代的生成器
    )
    for chunk in stream:
        delta = chunk.choices[0].delta.content
        if delta:  # 首块/尾块可能不含正文内容
            print(delta, end="", flush=True)
    print()


def main():
    models = list_local_models()
    if models is None:
        print_install_guide()
        return  # 正常退出，退出码 0

    if not any(m == CHAT_MODEL or m.startswith(f"{CHAT_MODEL}:") for m in models):
        print(f"Ollama 服务在线，但本机还没有模型 {CHAT_MODEL}（已安装：{models or '无'}）。")
        print(f"先执行：ollama pull {CHAT_MODEL}，然后重跑本脚本。")
        return

    print(f"检测到 Ollama 在线，使用模型 {CHAT_MODEL}\n")
    try:
        demo_chat()
    except Exception as exc:
        # 例如模型被删、服务中途退出等情况：给出排查方向，不让初学者面对裸堆栈
        print(f"调用失败：{exc}")
        print(f"排查：ollama list 确认 {CHAT_MODEL} 已安装；确认 Ollama 应用/服务正在运行。")
        sys.exit(1)


if __name__ == "__main__":
    main()
