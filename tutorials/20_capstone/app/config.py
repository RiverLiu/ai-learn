"""双服务配置：聊天模型与向量模型可以来自不同的服务商。

国内常见的落地方式是"聊天一家、向量一家"——比如聊天用月之暗面 Kimi，
向量用阿里云百炼。各家接口都兼容 OpenAI 协议，因此配置分两组：

- 聊天：OPENAI_API_KEY / OPENAI_BASE_URL / MODEL_NAME
- 向量：EMBEDDING_API_KEY / EMBEDDING_BASE_URL / EMBEDDING_MODEL

向量服务的凭证缺省时回落到 OPENAI_API_KEY / OPENAI_BASE_URL——
聊天和向量用同一家服务商时，只需配置一组 OPENAI_* 即可。
"""

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

# 加载 .env：优先本模块目录（tutorials/20_capstone/.env），其次向上查找（如项目根目录）
load_dotenv(Path(__file__).parent.parent / ".env")
load_dotenv()


@dataclass(frozen=True)
class ChatConfig:
    api_key: str
    base_url: str | None
    model: str


@dataclass(frozen=True)
class EmbeddingConfig:
    api_key: str
    base_url: str | None
    model: str


def load_chat_config() -> ChatConfig:
    """读取聊天服务配置（OPENAI_* 一组）。"""
    api_key = os.getenv("OPENAI_API_KEY", "")
    if not api_key:
        raise RuntimeError("缺少 OPENAI_API_KEY，请参考 tutorials/20_capstone/.env.example 配置")
    return ChatConfig(
        api_key=api_key,
        base_url=os.getenv("OPENAI_BASE_URL") or None,
        model=os.getenv("MODEL_NAME", "gpt-4o-mini"),
    )


def load_embedding_config() -> EmbeddingConfig:
    """读取向量服务配置，凭证缺省时回落到聊天服务的 OPENAI_*。"""
    api_key = os.getenv("EMBEDDING_API_KEY") or os.getenv("OPENAI_API_KEY", "")
    if not api_key:
        raise RuntimeError(
            "缺少 EMBEDDING_API_KEY（或 OPENAI_API_KEY），"
            "请参考 tutorials/20_capstone/.env.example 配置"
        )
    return EmbeddingConfig(
        api_key=api_key,
        base_url=os.getenv("EMBEDDING_BASE_URL") or os.getenv("OPENAI_BASE_URL") or None,
        model=os.getenv("EMBEDDING_MODEL", "text-embedding-3-small"),
    )
