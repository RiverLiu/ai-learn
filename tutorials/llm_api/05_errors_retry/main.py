"""错误处理、指数退避重试与成本估算。

真实网络环境什么都会发生：密钥配错、模型名写错、被限速、超时……
本章做三件事：
1. 故意触发一个错误，看看异常长什么样；
2. 写一个带指数退避的重试封装（生产代码必备）；
3. 用 response.usage 估算一次调用花多少钱。

运行（在仓库根目录）：uv run tutorials/llm_api/05_errors_retry/main.py
"""

import os
import time

import openai
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()  # 向上查找项目根目录 .env
client = OpenAI()  # 自动读取 OPENAI_API_KEY / OPENAI_BASE_URL
MODEL = os.getenv("MODEL_NAME", "gpt-4o-mini")

# 值得重试的错误（过一会儿可能自己好）：限速、超时、断线、服务端 5xx
RETRYABLE_ERRORS = (
    openai.RateLimitError,       # 429 请求太频繁 / 额度不足
    openai.APITimeoutError,      # 超时
    openai.APIConnectionError,   # 网络断连
    openai.InternalServerError,  # 500+ 服务端故障
)
# 不值得重试的错误（重试一百次也一样）：401 密钥错、404 模型名错、400 参数错，
# 这些会直接抛出，交给人去修配置。


# ---------------------------------------------------------------------------
# 1. 故意触发一个错误：不存在的模型名
# ---------------------------------------------------------------------------
def error_types_demo():
    """看清异常的类型、HTTP 状态码和错误信息——排查问题的第一手资料。"""
    try:
        client.chat.completions.create(
            model="definitely-not-a-model",  # 故意写错的模型名
            messages=[{"role": "user", "content": "你好"}],
        )
    except openai.APIStatusError as e:  # 所有带 HTTP 状态码的错误都继承自它
        print(f"捕获异常类型：{type(e).__name__}")
        print(f"HTTP 状态码：{e.status_code}")
        print(f"错误信息：{e.message}")
        print("→ 这类错误是配置问题，重试无意义，应该立即报错给人看。")


# ---------------------------------------------------------------------------
# 2. 带指数退避的重试封装
# ---------------------------------------------------------------------------
def chat_with_retry(a_client: OpenAI, max_attempts: int = 3, base_delay: float = 1.0, **kwargs):
    """失败自动重试，等待时间按 1s → 2s → 4s… 翻倍（指数退避），避免雪上加霜。

    注意：OpenAI SDK 自带重试（默认 2 次）。这里为教学演示，
    调用方传入的 client 一般会设 max_retries=0，把重试权完全交给我们自己。
    """
    for attempt in range(1, max_attempts + 1):
        try:
            return a_client.chat.completions.create(**kwargs)
        except RETRYABLE_ERRORS as e:
            if attempt == max_attempts:
                print(f"  第 {attempt} 次尝试仍失败（{type(e).__name__}），放弃并抛出异常")
                raise
            delay = base_delay * (2 ** (attempt - 1))  # 指数退避：1s → 2s → 4s…
            print(f"  第 {attempt} 次失败（{type(e).__name__}），{delay:.0f}s 后重试…")
            time.sleep(delay)
        # 不可重试的错误（401/404/400 等）不匹配上面的 except，直接抛给调用方


def retry_demo():
    """用"模拟错误"演示重试逻辑（不去真触发 429，那要花真金白银）。

    演示 A：把超时设成 0.001 秒——每次请求必然超时（可重试错误），
            能看到 1s → 2s 的退避节奏，3 次后放弃。
    演示 B：模型名不存在（404，不可重试）——不重试，立即抛出。
    """
    print("【演示 A：必然超时 → 退避重试 → 放弃】")
    impatient_client = OpenAI(timeout=0.001, max_retries=0)
    try:
        chat_with_retry(
            impatient_client,
            model=MODEL,
            messages=[{"role": "user", "content": "你好"}],
        )
    except openai.APITimeoutError:
        print("  最终结果：重试耗尽，调用失败（生产中应记录日志并告警）")

    print("\n【演示 B：模型名错误 → 不可重试 → 立即抛出】")
    strict_client = OpenAI(max_retries=0)
    try:
        chat_with_retry(
            strict_client,
            model="definitely-not-a-model",
            messages=[{"role": "user", "content": "你好"}],
        )
    except openai.APIStatusError as e:
        print(f"  没有重试，直接抛出 {type(e).__name__}（HTTP {e.status_code}）——配置错误就该这样")

    print("\n【演示 C：正常调用 → 一次成功，不触发任何重试】")
    answer = chat_with_retry(
        client,  # 正常 client，用默认配置即可
        model=MODEL,
        messages=[{"role": "user", "content": "用一句话说明为什么要给 API 调用加重试。"}],
    )
    print(f"  成功拿到回答：{answer.choices[0].message.content}")


# ---------------------------------------------------------------------------
# 3. 成本估算：用 usage 算一次调用花多少钱
# ---------------------------------------------------------------------------
def cost_demo():
    """token 单价以服务商官网为准，这里用 gpt-4o-mini 的公开价做示例。"""
    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": "你是一个简洁的助手。"},
            {"role": "user", "content": "用三句话介绍杭州。"},
        ],
    )
    u = response.usage
    # 示例单价（美元 / 每 token）：gpt-4o-mini 官网价 输入 $0.15、输出 $0.60 / 百万 token
    # 换成你实际用的服务商价格即可；注意思考型模型的"推理 token"也按输出计费
    price_input = 0.15 / 1_000_000
    price_output = 0.60 / 1_000_000
    cost = u.prompt_tokens * price_input + u.completion_tokens * price_output

    print(f"输入 {u.prompt_tokens} token × ${price_input:.2e}")
    print(f"输出 {u.completion_tokens} token × ${price_output:.2e}")
    print(f"本次调用估算成本：${cost:.6f}（约 ¥{cost * 7.2:.6f}）")
    print("→ 单次不到一分钱，但日均百万次调用的产品必须盯住这个数字。")


def main():
    print(f"（使用模型：{MODEL}）\n")

    print("===== 1. 故意触发一个错误 =====")
    error_types_demo()

    print("\n===== 2. 指数退避重试 =====")
    retry_demo()

    print("\n===== 3. 成本估算 =====")
    cost_demo()


if __name__ == "__main__":
    main()
