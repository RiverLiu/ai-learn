"""纵深防御：假设提示词防线终将被突破，在工程层再布三道防线。

提示词注入目前没有"银弹"。本脚本用纯代码演示三类不依赖模型自觉的兜底措施：
1. 数据脱敏：把用户输入里的 PII（手机号、邮箱、身份证）先漂白再进 LLM；
2. 工具权限门：敏感工具必须过白名单 + 人工审批，模型只能"建议"不能"执行"；
3. 密钥卫生：扫描代码里是否误写了 API key，检查 .env 是否被 .gitignore 保护。

运行（在仓库根目录）：uv run tutorials/17_security/03_defense_in_depth/main.py
"""

import os
import re
import sys
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()  # 读取 .env：OPENAI_API_KEY / OPENAI_BASE_URL / MODEL_NAME

client = OpenAI()
MODEL = os.getenv("MODEL_NAME", "gpt-4o-mini")
REPO_ROOT = Path(__file__).resolve().parents[3]

# ---------------------------------------------------------------------------
# 1. 数据脱敏：PII 不进 LLM
# ---------------------------------------------------------------------------
# 生产环境应使用更完备的脱敏库（如 presidio），教学用正则覆盖最常见三类
# 注意顺序：先匹配身份证号，再匹配手机号，避免手机正则在长数字串里“咬”到身份证
PII_PATTERNS = [
    (re.compile(r"\b\d{17}[\dXx]|\d{15}\b"), "[ID_CARD]"),  # 身份证（18 位或 15 位）
    (re.compile(r"(?<![0-9])1[3-9]\d{9}(?![0-9])"), "[PHONE]"),  # 中国手机号，前后不能是数字
    (re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b"), "[EMAIL]"),
]


def redact_pii(text: str) -> str:
    """把常见 PII 替换为占位符，返回漂白后的文本。"""
    for pattern, placeholder in PII_PATTERNS:
        text = pattern.sub(placeholder, text)
    return text


def safe_intent_summary(user_message: str) -> str:
    """示例：脱敏后再发给模型做意图摘要，确保模型永远看不到原始 PII。"""
    clean = redact_pii(user_message)
    prompt = (
        "你是客服助手。请用一句话总结以下用户消息的意图，不要复述任何联系方式或身份信息。\n\n"
        f"用户消息：{clean}"
    )
    try:
        resp = client.chat.completions.create(
            model=MODEL,
            messages=[{"role": "user", "content": prompt}],
        )
        return resp.choices[0].message.content or "（模型未返回内容）"
    except Exception as exc:
        return f"（调用模型失败：{exc}）"


# ---------------------------------------------------------------------------
# 2. 工具权限门：模型只能建议，执行必须过审批
# ---------------------------------------------------------------------------
class ToolGate:
    """工具执行门：白名单 + 风险分级 + 人工审批。"""

    # 允许模型调用的工具名
    WHITELIST = {"search_knowledge", "create_ticket", "send_email", "refund", "delete_account"}
    # 高风险工具：即使模型想调用，也必须先取得人工审批
    HIGH_RISK = {"refund", "delete_account"}

    def __init__(self):
        # 已审批的请求 ID（真实系统里由运营后台写入）
        self.approved_ids: set[str] = set()

    def approve(self, request_id: str) -> None:
        """运营人员/审批系统显式批准某个请求。"""
        self.approved_ids.add(request_id)

    def execute(self, request_id: str, tool: str, args: dict) -> str:
        if tool not in self.WHITELIST:
            return f"❌ 拒绝：工具 {tool} 不在白名单"
        if tool in self.HIGH_RISK and request_id not in self.approved_ids:
            return (
                f"⏸ 高风险工具 {tool} 被拦截，等待人工审批（请求 ID: {request_id}）。\n"
                f"   模型可建议执行，但代码层不会真正调用。"
            )
        # 这里才是真正调用外部系统的位置
        return f"✅ 允许执行 {tool}({args})"


def demo_tool_gate():
    gate = ToolGate()
    requests = [
        ("req-1", "search_knowledge", {"query": "如何申请发票"}),
        ("req-2", "refund", {"order_id": "ORD-2026-001", "reason": "用户不满意"}),
        ("req-3", "hack_database", {"table": "users"}),  # 不在白名单
    ]
    print("--- 默认状态：无人工审批 ---")
    for rid, tool, args in requests:
        print(gate.execute(rid, tool, args))

    print("\n--- 运营人员批准 req-2 后 ---")
    gate.approve("req-2")
    for rid, tool, args in requests:
        if tool in ToolGate.HIGH_RISK or tool not in ToolGate.WHITELIST:
            print(gate.execute(rid, tool, args))


# ---------------------------------------------------------------------------
# 3. 密钥卫生：代码里不能写 key，.env 必须被 gitignore
# ---------------------------------------------------------------------------
KEY_PATTERNS = [
    re.compile(r"sk-[A-Za-z0-9]{20,}"),                # OpenAI / Moonshot 风格 key
    re.compile(r"OPENAI_API_KEY\s*=\s*['\"][^'\"]+['\"]"),
    re.compile(r"API_KEY\s*=\s*['\"][^'\"]{16,}['\"]"),
]


def scan_hardcoded_keys(root: Path) -> list[Path]:
    """扫描代码目录，返回包含疑似硬编码密钥的文件路径。"""
    bad_files = []
    for path in root.rglob("*.py"):
        text = path.read_text(encoding="utf-8", errors="ignore")
        if any(p.search(text) for p in KEY_PATTERNS):
            bad_files.append(path)
    return bad_files


def check_env_gitignore() -> bool:
    """检查 .env 是否被 .gitignore 忽略。"""
    gitignore = root / ".gitignore" if (root := REPO_ROOT).exists() else None
    if not gitignore:
        return False
    for line in gitignore.read_text(encoding="utf-8").splitlines():
        if line.strip() in {".env", "*.env", ".env*"}:
            return True
    return False


def demo_key_hygiene():
    print("\n--- 密钥卫生扫描 ---")
    bad = scan_hardcoded_keys(REPO_ROOT / "tutorials")
    if bad:
        print("⚠️  以下文件疑似包含硬编码密钥，请检查：")
        for p in bad:
            print(f"   {p.relative_to(REPO_ROOT)}")
    else:
        print("✅ 未在代码中扫描到明显的 API key 硬编码模式")

    if check_env_gitignore():
        print("✅ .env 已被 .gitignore 保护")
    else:
        print("⚠️  .env 似乎未被 .gitignore 忽略，请立即添加 `.env` 一行")


# ---------------------------------------------------------------------------
def main():
    print("=" * 60)
    print("防线 1：数据脱敏")
    print("=" * 60)
    raw = (
        "我叫张三，手机 13800138000，邮箱 zhangsan@example.com，"
        "身份证 110101199001011234。我想退款。"
    )
    print(f"原始输入：{raw}")
    print(f"脱敏后：  {redact_pii(raw)}")
    print("\n脱敏后调用模型做意图摘要：")
    print(safe_intent_summary(raw))

    print("\n" + "=" * 60)
    print("防线 2：工具权限门")
    print("=" * 60)
    demo_tool_gate()

    print("\n" + "=" * 60)
    print("防线 3：密钥卫生")
    print("=" * 60)
    demo_key_hygiene()

    print("\n" + "=" * 60)
    print("结论")
    print("=" * 60)
    print("提示词加固只是第一道门槛；真正的安全来自：")
    print("  1. 敏感数据不进模型（脱敏/最小化）；")
    print("  2. 模型只能建议，执行敏感操作必须过审批；")
    print("  3. 密钥、内部代号不进提示词和代码仓库。")


if __name__ == "__main__":
    main()
