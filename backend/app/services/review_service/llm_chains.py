"""ChatOpenAI 与 Map / Reduce / Final 的 LCEL 链（无跨请求记忆）。"""

from __future__ import annotations

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

from app.config import Settings
from app.services.review_service.batching import MAP_USER_PREFIX

MAP_SYSTEM = """You are a biomedical literature synthesis assistant. Given a batch of article titles and abstracts (English or mixed languages), produce factual, review-style intermediate notes:
1. A bullet list of evidence-based key points only (no fabrication, no speculation). Use precise biomedical terminology where appropriate. Prefix each line with "- ".
2. One line starting with "Themes: " followed by 2-4 short English theme phrases separated by "; ".

Write in English. Use neutral academic register (avoid colloquialisms). Do not use markdown headings, bold, italics, or the asterisk character "*" anywhere in the output."""

REDUCE_SYSTEM = """You consolidate intermediate summaries from a biomedical literature review pipeline. Merge overlapping content into a concise bullet list (each line starts with "- "). Keep one line "Themes: ..." with 2-4 English theme phrases separated by "; ". No fabrication. English only. Neutral academic tone. Do not use the asterisk character "*" or markdown emphasis."""

FINAL_SYSTEM = """你是生物医学领域文献综述写作助手，帮助用户快速总结文献内容。仅根据用户提供的「中间摘要与主题」归纳与综合，勿编造文献中未出现的结论或数据。

输出须为简体中文，且必须使用 Markdown：
1. 开篇用一至两段做总述，不超过50字。
2. 随后用二级标题「## 」逐条分述每一要点，不超过4个二级标题；每节内可用以「- 」开头的列表（不超过3条）补充细节。
3. 不要使用一级标题「#」。需要强调的关键术语可使用加粗「**术语**」。
4. 列表请使用「- 」，不要使用「*」作为列表符号。

篇幅：全文以汉字计**目标约 400 字**（可略多，但不宜过长）。**优先保证每一句、每一段语义完整**，不得写出半截句子或残缺段落；通过简练措辞控制长度，而非删到句中停止。文末不得以省略号收尾。"""

DIRECT_SYSTEM = """你是生物医学领域文献综述写作助手，帮助用户快速总结文献内容。仅根据下方「文献题录全文」归纳与综合，勿编造文献中未出现的结论或数据。

输出须为简体中文，且必须使用 Markdown：
1. 开篇用一至两段做总述，不超过50字。
2. 随后用二级标题「## 」逐条分述每一要点，不超过4个二级标题 ；每节内可用以「- 」开头的列表（不超过3条）。
3. 不要使用一级标题「#」。需要强调的关键术语可使用加粗「**术语**」。
4. 列表请使用「- 」，不要使用「*」作为列表符号。

篇幅：全文以汉字计**目标约 400 字**（可略多，但不宜过长）。**优先保证每一句、每一段语义完整**，不得写出半截句子；通过简练措辞控制长度。总述与分述均须简练。文末不得以省略号收尾。"""


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
    return prompt | llm.bind(max_tokens=720, temperature=0.25) | StrOutputParser()


def build_direct_chain(llm: ChatOpenAI):
    """题录总篇幅较小时一次性生成综述，跳过 Map/Reduce。"""
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", DIRECT_SYSTEM),
            (
                "human",
                "用户检索式：{query}\n\n"
                "统计摘要：共检索 {total_hits} 条，"
                "分析 {analyzed_count} 条；"
                "期刊本地匹配率 {journal_match_rate}。\n\n"
                "以下为文献题录全文（Title + Abstract，仅依据这些内容归纳，"
                "勿补充文献中未出现的信息）：\n\n"
                "{corpus_text}",
            ),
        ]
    )
    return prompt | llm.bind(max_tokens=720, temperature=0.25) | StrOutputParser()
