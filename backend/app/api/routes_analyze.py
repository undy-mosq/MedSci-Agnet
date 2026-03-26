"""分析接口：PubMed 检索 + 统计 + 词云；综述见 POST /api/review。"""

import json
import logging
from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException

from app.config import Settings, get_settings
from app.models.schemas import (
    AnalyzeRequest,
    AnalyzeResponse,
    ReviewPayload,
    ReviewRequest,
    WordCloudItem,
)
from app.services.analytics_service import (
    attach_metrics,
    build_corpus_stats,
    top100_if_recent_years,
)
from app.services.metrics_service import get_metrics_repository
from app.services.pubmed_service import PubMedError, search_and_fetch
from app.services.review_service import build_review
from app.services.text_mining_service import build_word_frequencies

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["analyze"])


def get_app_settings() -> Settings:
    """依赖注入配置。"""
    return get_settings()


@router.post("/analyze", response_model=AnalyzeResponse)
def post_analyze(
    body: AnalyzeRequest,
    settings: Annotated[Settings, Depends(get_app_settings)],
) -> AnalyzeResponse:
    """检索 PubMed 并返回带指标的分析结果。"""
    capped = min(body.max_results, settings.max_analyze_results)
    try:
        records, total_hits = search_and_fetch(body.query.strip(), capped, settings)
    except PubMedError as e:
        logger.warning("PubMed 错误: %s", e)
        raise HTTPException(status_code=502, detail=str(e)) from e

    repo = get_metrics_repository()
    articles = attach_metrics(records, repo.lookup)
    stats = build_corpus_stats(articles, total_hits)
    top100 = top100_if_recent_years(articles, years=5)
    texts: list[str] = []
    for r in records:
        t = (r.get("title") or "") + " " + (r.get("abstract") or "")
        texts.append(t)
    wf = build_word_frequencies(texts, top_n=100)
    wordcloud = [WordCloudItem(word=w, weight=c) for w, c in wf]

    return AnalyzeResponse(
        articles=articles,
        stats=stats,
        top100_if_5y=top100,
        wordcloud=wordcloud,
        review=None,
    )


@router.post("/review", response_model=ReviewPayload)
def post_review(
    body: ReviewRequest,
    settings: Annotated[Settings, Depends(get_app_settings)],
) -> ReviewPayload:
    """基于已检索的 stats 与题录生成综述（LLM 或模板回退），不重复请求 PubMed。"""
    review_articles = top100_if_recent_years(body.articles, years=5)
    raw_records: list[dict[str, Any]] = [
        {"title": a.title, "abstract": a.abstract or ""} for a in review_articles
    ]
    return build_review(body.query.strip(), body.stats, raw_records, settings)


@router.get("/journal-metrics")
def get_journal_metrics(
    settings: Annotated[Settings, Depends(get_app_settings)],
) -> list[dict[str, Any]]:
    """返回本地期刊指标 JSON 数组（与配置的 `journal_metrics_path` 文件一致）。"""
    path = settings.journal_metrics_path
    if not path.is_file():
        raise HTTPException(status_code=404, detail="期刊指标文件不存在")
    try:
        raw = path.read_text(encoding="utf-8")
    except OSError as e:
        logger.warning("读取期刊指标失败: %s", e)
        raise HTTPException(status_code=500, detail="读取期刊指标失败") from e
    try:
        data = json.loads(raw)
    except json.JSONDecodeError as e:
        raise HTTPException(status_code=500, detail="期刊指标 JSON 无效") from e
    if isinstance(data, dict) and "journals" in data:
        inner = data["journals"]
        return inner if isinstance(inner, list) else []
    if isinstance(data, list):
        return data
    return []


@router.get("/ping")
def ping() -> dict[str, str]:
    """轻量探活。"""
    return {"message": "pong"}
