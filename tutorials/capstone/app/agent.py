"""LangGraph Agent：检索工具 + 退款估算工具，checkpointer 多轮记忆。

与 langgraph 教程同一思路：create_agent 一行构建"LLM 提议 → 执行工具 →
再提议"的 ReAct 循环；MemorySaver + thread_id 实现线程隔离的多轮记忆
（生产环境把 MemorySaver 换成 SqliteSaver/PostgresSaver 即可落盘）。
"""

import threading

from langchain.agents import create_agent
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.memory import MemorySaver

from .config import load_chat_config
from .knowledge import KnowledgeBase

SYSTEM_PROMPT = (
    "你是「云雀笔记」的智能客服助手，回答用户关于产品的问题。规则：\n"
    "1. 涉及产品功能、价格、政策的问题，必须先调用 search_knowledge 检索知识库，"
    "基于检索结果回答，不要凭印象作答；回答结尾用【来源：xxx】注明依据的文档。\n"
    "2. 涉及退款金额估算的问题，先确认用户的付费方案和已使用天数，"
    "再调用 calc_refund 计算，并解释计算依据。\n"
    "3. 知识库里没有的信息就明说不知道、引导用户联系人工客服，不要编造；"
    "与云雀笔记无关的问题礼貌拒绝。\n"
    "4. 回答简洁口语化，像真人客服一样。"
)

_kb: KnowledgeBase | None = None
_agent = None
_lock = threading.Lock()


@tool
def search_knowledge(query: str) -> str:
    """在云雀笔记知识库中检索与问题相关的段落。输入应为简洁的检索词或问题。"""
    results = _kb.search(query, top_k=3)
    return "\n\n".join(
        f"【来源：{r['source']}】（相似度 {r['score']:.2f}）\n{r['text']}"
        for r in results
    )


# 与 data/knowledge_base/pricing.md 一致的定价：专业版 18 元/月、168 元/年，团队版 45 元/人/月
_PLANS = {
    "pro_monthly": {"name": "专业版（按月付费）", "price": 18.0, "yearly": False},
    "pro_yearly": {"name": "专业版（按年付费）", "price": 168.0, "yearly": True},
    "team_monthly": {"name": "团队版（每成员按月付费）", "price": 45.0, "yearly": False},
}


@tool
def calc_refund(days_used: int, plan: str) -> str:
    """按云雀笔记退款政策估算可退金额。

    days_used 为已使用天数；plan 为 pro_monthly（专业版按月）/
    pro_yearly（专业版按年）/ team_monthly（团队版按月，按每成员计）。
    政策：7 天内无理由全额退款；超过 7 天，按年付费按剩余月份折算，
    按月付费不支持中途退款。
    """
    if days_used < 0:
        return "错误：days_used 不能为负数"
    plan_info = _PLANS.get(plan)
    if plan_info is None:
        return f"错误：未知方案 {plan!r}，可选：{', '.join(_PLANS)}"
    name, price, yearly = plan_info["name"], plan_info["price"], plan_info["yearly"]

    if days_used <= 7:
        return (
            f"{name}，已使用 {days_used} 天，在 7 天无理由退款期内，"
            f"可全额退款 {price:.2f} 元，申请后 3 个工作日内原路退回。"
        )
    if not yearly:
        return (
            f"{name}，已使用 {days_used} 天，超过 7 天无理由退款期；"
            f"按月付费不支持中途退款，可退 0 元。"
        )
    months_used = -(-days_used // 30)  # 已消耗月份，向上取整
    remaining = max(0, 12 - months_used)
    refund = price * remaining / 12
    return (
        f"{name}，已使用 {days_used} 天（按 {months_used} 个月计），"
        f"超过 7 天无理由退款期；按年付费按剩余 {remaining} 个月折算，"
        f"可退 {refund:.2f} 元（{price:.0f} × {remaining}/12）。"
    )


def get_agent():
    """构建并缓存 Agent。首次调用时加载知识库、调用向量接口构建索引，较慢。"""
    global _kb, _agent
    with _lock:
        if _agent is None:
            _kb = KnowledgeBase()
            chat = load_chat_config()
            model = ChatOpenAI(
                model=chat.model, api_key=chat.api_key, base_url=chat.base_url
            )
            _agent = create_agent(
                model,
                tools=[search_knowledge, calc_refund],
                system_prompt=SYSTEM_PROMPT,
                checkpointer=MemorySaver(),
            )
    return _agent
