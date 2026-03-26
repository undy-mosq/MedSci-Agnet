"""综述流水线：generate_llm_review（LCEL Map→可选 Reduce→Final）与 build_review。"""

from __future__ import annotations

import logging
from typing import Any

from app.config import Settings, get_settings
from app.models.schemas import CorpusStats, ReviewPayload
from app.services.review_service.batching import (
    batch_records_for_map,
    final_summaries_token_budget,
    format_record,
    needs_intermediate_reduce,
    split_text_by_token_budget,
)
from app.services.review_service.llm_chains import (
    build_direct_chain,
    build_final_chain,
    build_map_chain,
    build_reduce_chain,
    get_chat_llm,
)
from app.services.review_service.template import template_review

logger = logging.getLogger(__name__)

# 题录拼接总字符数低于此阈值时，单次调用生成综述，不走 Map/Reduce。
_CORPUS_DIRECT_MAX_CHARS = 5000


def _finalize_review_text(text: str) -> str:
    """仅去除首尾空白，不做字数截断，以免切断句子。"""
    return (text or "").strip()


def _reduce_until_final_fit(
    combined: str,
    model: str,
    reduce_chain,
    *,
    reserved_output: int = 1200,
) -> str:
    """中间摘要过长时多轮压缩，直至满足 Final 输入预算。"""
    max_rounds = 16
    round_idx = 0
    while needs_intermediate_reduce(
        combined,
        model,
        reserved_output=reserved_output,
    ):
        round_idx += 1
        if round_idx > max_rounds:
            logger.error("中间摘要压缩超过最大轮次，放弃 LLM 综述。")
            raise RuntimeError("reduce rounds exceeded")

        budget = final_summaries_token_budget(
            model,
            reserved_output=reserved_output,
        )
        chunk_tokens = max(2048, budget // 2)
        chunks = split_text_by_token_budget(combined, model, chunk_tokens)
        merged_parts: list[str] = []
        for ch in chunks:
            out = reduce_chain.invoke({"chunk_text": ch})
            merged_parts.append((out or "").strip())
        combined = "\n\n---\n\n".join(p for p in merged_parts if p)
        if not combined:
            raise RuntimeError("empty after reduce")
    return combined


def generate_llm_review(
    query: str,
    stats: CorpusStats,
    raw_records: list[dict[str, Any]],
    settings: Settings | None = None,
) -> str | None:
    """LCEL Map → 可选 Reduce → Final，成功返回中文综述；失败返回 None。"""
    settings = settings or get_settings()
    key = settings.llm_api_key
    if not key or not str(key).strip():
        return None

    model = settings.llm_model

    try:
        llm = get_chat_llm(settings)
        corpus_text = "".join(format_record(r) for r in raw_records)
        if not corpus_text.strip():
            return None

        journal_match_rate = f"{stats.journal_match_rate:.2%}"
        stats_ctx = {
            "query": query,
            "total_hits": stats.total_hits,
            "analyzed_count": stats.analyzed_count,
            "journal_match_rate": journal_match_rate,
        }

        if len(corpus_text) < _CORPUS_DIRECT_MAX_CHARS:
            direct_chain = build_direct_chain(llm)
            final_text = direct_chain.invoke({**stats_ctx, "corpus_text": corpus_text})
            return _finalize_review_text(final_text)

        map_chain = build_map_chain(llm)
        reduce_chain = build_reduce_chain(llm)
        final_chain = build_final_chain(llm)

        batches = batch_records_for_map(raw_records, model)
        if not batches:
            return None

        map_outputs: list[str] = []
        for batch_text in batches:
            out = map_chain.invoke({"batch_text": batch_text})
            map_outputs.append((out or "").strip())

        combined = "\n\n---\n\n".join(s for s in map_outputs if s)
        if not combined:
            return None

        combined = _reduce_until_final_fit(
            combined,
            model,
            reduce_chain,
            reserved_output=1200,
        )

        final_text = final_chain.invoke({**stats_ctx, "summaries": combined})
        return _finalize_review_text(final_text)
    except Exception as e:
        logger.error("LLM 综述流水线失败: %s", e, exc_info=True)
        return None


def build_review(
    query: str,
    stats: CorpusStats,
    raw_records: list[dict[str, Any]],
    settings: Settings | None = None,
) -> ReviewPayload:
    """模板或 LLM 综述（LLM 失败时回退模板，与原行为一致）。"""
    settings = settings or get_settings()
    snippets = [
        str(r.get("abstract") or r.get("title") or "") for r in raw_records
    ]
    llm_text = generate_llm_review(query, stats, raw_records, settings)
    if llm_text:
        return ReviewPayload(text=llm_text, mode="llm")
    return ReviewPayload(text=template_review(stats, snippets), mode="template")
