"""ChatOpenAI 与 Map / Reduce / Final 的 LCEL 链（无跨请求记忆）。"""

from __future__ import annotations

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

from app.config import Settings
from app.services.review_service.batching import MAP_USER_PREFIX

MAP_SYSTEM = """You are a biomedical literature assistant. Given a batch of article titles and abstracts (English or mixed languages), produce:
1. A bullet list of factual key points only (no fabrication). Prefix each line with "- ".
2. A single line starting with "Themes: " followed by 2-4 short English theme phrases separated by "; ".

Use English for this intermediate output. Do not add markdown headings."""

REDUCE_SYSTEM = """You are summarizing intermediate batch summaries from a literature review pipeline. Merge overlapping content into a concise bullet list (prefix "- "). Add one line "Themes: ..." with 2-4 English theme phrases separated by "; ". No fabrication. English only."""

FINAL_SYSTEM = """你是生物医学文献分析助手。只根据用户提供的「中间摘要与主题」归纳，勿编造数据。输出简体中文，约 500 字，使用分点列表（- 开头），不要 Markdown 标题符号。"""


def get_chat_llm(settings: Settings) -> ChatOpenAI:
    """OpenAI 兼容 Chat 接口，超时与现有 httpx 120s 一致。"""
    return ChatOpenAI(
        model=settings.llm_model,
        api_key=(settings.llm_api_key or "").strip(),
        base_url=settings.llm_api_base.rstrip("/"),
        timeout=120.0,
        temperature=0.3,
    )


def build_map_chain(llm: ChatOpenAI):
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", MAP_SYSTEM),
            ("human", MAP_USER_PREFIX + "{batch_text}"),
        ]
    )
    return prompt | llm.bind(max_tokens=2048) | StrOutputParser()


def build_reduce_chain(llm: ChatOpenAI):
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", REDUCE_SYSTEM),
            ("human", "{chunk_text}"),
        ]
    )
    return prompt | llm.bind(max_tokens=2048) | StrOutputParser()


def build_final_chain(llm: ChatOpenAI):
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", FINAL_SYSTEM),
            (
                "human",
                "用户检索式：{query}\n\n"
                "统计摘要：共检索 {total_hits} 条，"
                "分析 {analyzed_count} 条；"
                "期刊本地匹配率 {journal_match_rate}。\n\n"
                "以下为各批文献的归纳摘要与主题（仅依据这些内容归纳，"
                "勿补充文献中未出现的信息）：\n\n"
                "{summaries}",
            ),
        ]
    )
    return prompt | llm.bind(max_tokens=1200, temperature=0.3) | StrOutputParser()
