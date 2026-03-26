"""tiktoken 分批与单条题录格式化（预留 system/user 模板 token）。"""

from __future__ import annotations

import logging
from typing import Any

import tiktoken

logger = logging.getLogger(__name__)

MAP_SYSTEM_RESERVED = 450
MAP_USER_PREFIX = (
    "Below is one batch of biomedical article records for systematic synthesis. "
    "Each record is Title + Abstract.\n\n"
)
MAP_USER_SUFFIX = ""

FINAL_QUERY_STATS_RESERVED = 800


def encoding_for_model(model: str) -> tiktoken.Encoding:
    """按模型选择编码；无法匹配时使用 cl100k_base。"""
    try:
        return tiktoken.encoding_for_model(model)
    except KeyError:
        return tiktoken.get_encoding("cl100k_base")


def estimate_context_window(model: str) -> int:
    """粗略估计上下文窗口（用于 60%–70% 预算）。"""
    m = model.lower()
    if "gpt-4o" in m or "gpt-4-turbo" in m or "gpt-4-0125" in m:
        return 128000
    if "gpt-3.5" in m:
        return 16385
    if "gpt-4" in m:
        return 8192
    return 128000


def format_record(record: dict[str, Any]) -> str:
    """单条题录：Title + Abstract。"""
    title = (record.get("title") or "").strip()
    abstract = (record.get("abstract") or "").strip()
    return f"Title: {title}\nAbstract: {abstract}\n"


def _count_tokens(enc: tiktoken.Encoding, text: str) -> int:
    return len(enc.encode(text))


def map_reserved_system_user_tokens(model: str) -> int:
    """Map 轮：system + user 固定前缀/后缀的 token 预留。"""
    enc = encoding_for_model(model)
    return (
        MAP_SYSTEM_RESERVED
        + _count_tokens(enc, MAP_USER_PREFIX)
        + _count_tokens(enc, MAP_USER_SUFFIX)
    )


def map_batch_article_token_budget(
    model: str,
    *,
    reserved_output: int = 2048,
    context_fraction: float = 0.65,
) -> int:
    """单批「题录拼接」部分允许的最大 token 数。"""
    ctx = estimate_context_window(model)
    reserved_system_user = map_reserved_system_user_tokens(model)
    total_budget = int(ctx * context_fraction) - reserved_system_user - reserved_output
    return max(1024, total_budget)


def _truncate_record_text_to_tokens(
    enc: tiktoken.Encoding,
    record: dict[str, Any],
    max_tokens: int,
) -> str:
    """单条超长时截断摘要，保留标题。"""
    title = (record.get("title") or "").strip()
    abstract = (record.get("abstract") or "").strip()
    header = f"Title: {title}\nAbstract: "
    header_t = _count_tokens(enc, header)
    if header_t >= max_tokens:
        short = enc.decode(enc.encode(header)[: max(0, max_tokens - 10)]) + "…\n"
        logger.warning("单条题录标题过长，已截断以适配批次上限。")
        return short
    remain = max_tokens - header_t
    ab_tokens = enc.encode(abstract)
    if len(ab_tokens) <= remain:
        return f"{header}{abstract}\n"
    cut = enc.decode(ab_tokens[:remain]) + "…"
    logger.warning("单条题录摘要过长，已截断以适配批次上限。")
    return f"{header}{cut}\n"


def batch_records_for_map(
    records: list[dict[str, Any]],
    model: str,
    *,
    reserved_output: int = 2048,
    context_fraction: float = 0.65,
) -> list[str]:
    """按 token 贪心分批，返回每批拼接后的题录文本（供 Map prompt 使用）。"""
    enc = encoding_for_model(model)
    article_budget = map_batch_article_token_budget(
        model,
        reserved_output=reserved_output,
        context_fraction=context_fraction,
    )

    batches: list[str] = []
    current_parts: list[str] = []
    current_tokens = 0

    for r in records:
        block = format_record(r)
        t = _count_tokens(enc, block)
        if t > article_budget:
            block = _truncate_record_text_to_tokens(enc, r, article_budget)
            t = _count_tokens(enc, block)

        if current_parts and current_tokens + t > article_budget:
            batches.append("".join(current_parts))
            current_parts = [block]
            current_tokens = t
        else:
            current_parts.append(block)
            current_tokens += t

    if current_parts:
        batches.append("".join(current_parts))
    return batches


def count_tokens(text: str, model: str) -> int:
    enc = encoding_for_model(model)
    return _count_tokens(enc, text)


def split_text_by_token_budget(text: str, model: str, max_chunk_tokens: int) -> list[str]:
    """将长文本切成不超过 max_chunk_tokens 的块（按 token 边界）。"""
    enc = encoding_for_model(model)
    ids = enc.encode(text)
    if len(ids) <= max_chunk_tokens:
        return [text]
    chunks: list[str] = []
    i = 0
    while i < len(ids):
        chunk_ids = ids[i : i + max_chunk_tokens]
        chunks.append(enc.decode(chunk_ids))
        i += max_chunk_tokens
    return chunks


def final_summaries_token_budget(
    model: str,
    *,
    reserved_output: int = 1200,
    context_fraction: float = 0.65,
) -> int:
    """Final 用户消息中「summaries」部分允许的最大 token。"""
    ctx = estimate_context_window(model)
    # query、统计字段与固定说明的数量级预留（与 final prompt 模板一致的量级）
    overhead = max(FINAL_QUERY_STATS_RESERVED, 1500)
    total = int(ctx * context_fraction) - overhead - reserved_output
    return max(2048, total)


def needs_intermediate_reduce(
    combined_summaries: str,
    model: str,
    *,
    reserved_output: int = 1200,
) -> bool:
    return count_tokens(combined_summaries, model) > final_summaries_token_budget(
        model,
        reserved_output=reserved_output,
    )
