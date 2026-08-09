"""Resources 与 Prompts：MCP 的另外两种原语。"""

from mcp.server.fastmcp import FastMCP

mcp = FastMCP("resources-prompts-demo")

# ---- 模拟数据 ----
USERS = {
    "001": {"name": "小明", "role": "后端工程师", "city": "北京"},
    "002": {"name": "小红", "role": "算法工程师", "city": "上海"},
}


# ---- Resources：向应用暴露可读取的数据 ----


@mcp.resource("config://app")
def app_config() -> str:
    """静态 Resource：固定的 URI，返回应用配置信息。"""
    return "app_name=demo-app; version=1.0.0; env=development"


@mcp.resource("user://{user_id}/profile")
def user_profile(user_id: str) -> str:
    """Resource 模板：URI 中带参数，按用户 ID 返回资料。"""
    user = USERS.get(user_id)
    if user is None:
        raise ValueError(f"用户 {user_id} 不存在")
    return f"姓名：{user['name']}，职位：{user['role']}，城市：{user['city']}"


# ---- Prompts：预定义的提示词模板 ----


@mcp.prompt()
def translate_to_english(text: str) -> str:
    """把给定文本翻译成英文的提示词模板。"""
    return f"请将下面这段中文翻译成地道的英文，只输出译文：\n\n{text}"


@mcp.prompt()
def code_review(code: str, language: str = "python") -> str:
    """代码评审提示词模板，带默认参数。"""
    return (
        f"你是一位资深 {language} 工程师，请评审以下代码，"
        f"指出潜在 bug、性能问题和可读性改进建议：\n\n```{language}\n{code}\n```"
    )


if __name__ == "__main__":
    mcp.run()
