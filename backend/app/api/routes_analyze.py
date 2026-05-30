"""[2026-05-19] /api/analyze 本地指标 JOIN；MedSci 补全见 /api/metrics-enrichment。"""

import json
import logging
from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException, Query

from app.config import Settings, get_settings
from app.models.schemas import (
    AnalyzeRequest,
    AnalyzeResponse,
    MetricsEnrichmentCancelResponse,
    MetricsEnrichmentEntry,
    MetricsEnrichmentInfo,
    MetricsEnrichmentPollResponse,
    MetricsEnrichmentSyncResponse,
    ReviewPayload,
    ReviewRequest,
)
from app.services.analytics_service import attach_metrics, top100_if_recent_years
from app.services.metrics_enrichment import (
    cancel_job,
    collect_unknown_keys,
    create_job,
    drain_updates,
    get_job,
    run_sync_batch,
)
from app.services.metrics_service import get_metrics_repository
from app.services.pubmed_service import PubMedError, search_and_fetch
from app.services.review_service import build_review

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["analyze"])


def get_app_settings() -> Settings:
    """依赖注入配置。"""
    return get_settings()


def _build_enrichment_info(
    job: Any | None,
    pending_count: int,
    settings: Settings,
) -> MetricsEnrichmentInfo:
    """构造 analyze 响应中的 enrichment 字段。"""
    needs = pending_count > 0 and settings.medsci_enabled
    return MetricsEnrichmentInfo(
        job_id=job.job_id if job and needs else None,
        pending_count=pending_count,
        needs_enrichment=needs,
    )


@router.post("/analyze", response_model=AnalyzeResponse)
def post_analyze(
    body: AnalyzeRequest,
    settings: Annotated[Settings, Depends(get_app_settings)],
) -> AnalyzeResponse:
    """检索 PubMed 并返回带本地指标的分析结果（不访问 MedSci）。"""
    capped = min(body.max_results, settings.max_analyze_results)
    try:
        records, total_hits = search_and_fetch(body.query.strip(), capped, settings)
    except PubMedError as e:
        logger.warning("PubMed 错误: %s", e)
        raise HTTPException(status_code=502, detail=str(e)) from e

    repo = get_metrics_repository()
    articles = attach_metrics(records, repo.lookup)
    unknown = collect_unknown_keys(records, repo.lookup)
    job = create_job(unknown, medsci_enabled=settings.medsci_enabled)
    enrichment = _build_enrichment_info(job, len(unknown), settings)

    return AnalyzeResponse(
        articles=articles,
        total_hits=total_hits,
        review=None,
        enrichment=enrichment,
    )


@router.post(
    "/metrics-enrichment/{job_id}/sync",
    response_model=MetricsEnrichmentSyncResponse,
)
def post_metrics_enrichment_sync(
    job_id: str,
    settings: Annotated[Settings, Depends(get_app_settings)],
    limit: int | None = Query(default=None, ge=1, le=50),
) -> MetricsEnrichmentSyncResponse:
    """同步批处理 MedSci 补全（默认最多 medsci_batch_size 本）。"""
    if not settings.medsci_enabled:
        raise HTTPException(status_code=503, detail="MedSci 补全已禁用")
    if get_job(job_id) is None:
        raise HTTPException(status_code=404, detail="补全任务不存在")
    try:
        raw = run_sync_batch(job_id, limit=limit, settings=settings)
    except KeyError:
        raise HTTPException(status_code=404, detail="补全任务不存在") from None
    except ValueError as e:
        msg = str(e)
        if msg == "completed":
            raise HTTPException(status_code=409, detail="任务已完成") from e
        if msg == "cancelled":
            raise HTTPException(status_code=409, detail="任务已取消") from e
        raise HTTPException(status_code=400, detail=msg) from e

    entries = [MetricsEnrichmentEntry.model_validate(e) for e in raw["new_entries"]]
    return MetricsEnrichmentSyncResponse(
        job_id=raw["job_id"],
        status=raw["status"],
        sync_enriched_count=raw["sync_enriched_count"],
        pending_count=raw["pending_count"],
        failed_count=raw["failed_count"],
        seq=raw["seq"],
        new_entries=entries,
        background_started=raw["background_started"],
    )


@router.get(
    "/metrics-enrichment/{job_id}",
    response_model=MetricsEnrichmentPollResponse,
)
def get_metrics_enrichment(
    job_id: str,
    since_seq: int = Query(default=0, ge=0),
) -> MetricsEnrichmentPollResponse:
    """轮询补全增量。"""
    try:
        raw = drain_updates(job_id, since_seq=since_seq)
    except KeyError:
        raise HTTPException(status_code=404, detail="补全任务不存在") from None
    entries = [MetricsEnrichmentEntry.model_validate(e) for e in raw["new_entries"]]
    return MetricsEnrichmentPollResponse(
        job_id=raw["job_id"],
        status=raw["status"],
        pending_count=raw["pending_count"],
        failed_count=raw["failed_count"],
        seq=raw["seq"],
        new_entries=entries,
    )


@router.post(
    "/metrics-enrichment/{job_id}/cancel",
    response_model=MetricsEnrichmentCancelResponse,
)
def post_metrics_enrichment_cancel(job_id: str) -> MetricsEnrichmentCancelResponse:
    """取消后台补全。"""
    try:
        raw = cancel_job(job_id)
    except KeyError:
        raise HTTPException(status_code=404, detail="补全任务不存在") from None
    return MetricsEnrichmentCancelResponse(
        job_id=raw["job_id"],
        status="cancelled",
        pending_count=raw["pending_count"],
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
