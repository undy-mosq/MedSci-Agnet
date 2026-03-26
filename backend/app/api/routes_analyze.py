"""分析接口：PubMed 检索 + 统计 + 词云 + 综述。"""

import logging
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException

from app.config import Settings, get_settings
from app.models.schemas import AnalyzeRequest, AnalyzeResponse, WordCloudItem
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
    wf = build_word_frequencies(texts, top_n=200)
    wordcloud = [WordCloudItem(word=w, weight=c) for w, c in wf]
    review = build_review(body.query.strip(), stats, records, settings)

    return AnalyzeResponse(
        articles=articles,
        stats=stats,
        top100_if_5y=top100,
        wordcloud=wordcloud,
        review=review,
    )


@router.get("/ping")
def ping() -> dict[str, str]:
    """轻量探活。"""
    return {"message": "pong"}
