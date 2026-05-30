"""[2026-05-19] MedSci 指标补全：sync + 后台队列 + poll；空闲自动取消。"""

from __future__ import annotations

import logging
import threading
import time
import uuid
from dataclasses import dataclass, field
from typing import Any, Literal

from app.config import Settings, get_settings
from app.services.medsci_service import enrich_one_journal
from app.services.metrics_service import (
    CompositeMetricsRepository,
    build_metrics_row_from_medsci,
    get_metrics_repository,
    has_metrics_match,
)

logger = logging.getLogger(__name__)

JobStatus = Literal["running", "completed", "cancelled"]


@dataclass
class JournalKey:
    """待补全刊键。"""

    issn: str | None
    journal_title: str | None

    def as_tuple(self) -> tuple[str | None, str | None]:
        return (self.issn, self.journal_title)


@dataclass
class EnrichmentUpdate:
    """单次写入的增量条目（含序号）。"""

    seq: int
    entry: dict[str, Any]


@dataclass
class EnrichmentJob:
    """内存补全任务。"""

    job_id: str
    pending: list[JournalKey] = field(default_factory=list)
    failed_count: int = 0
    seq: int = 0
    status: JobStatus = "running"
    updates: list[EnrichmentUpdate] = field(default_factory=list)
    background_started: bool = False
    background_running: bool = False
    cancelled: bool = False
    last_client_at: float = field(default_factory=time.monotonic)
    _lock: threading.Lock = field(default_factory=threading.Lock, repr=False)

    @property
    def pending_count(self) -> int:
        return len(self.pending)


_jobs: dict[str, EnrichmentJob] = {}
_jobs_lock = threading.Lock()


def collect_unknown_keys(
    records: list[dict[str, Any]],
    lookup: Any,
) -> list[JournalKey]:
    """从 PubMed 记录收集未命中指标的去重刊键。

    函数功能：筛出需 MedSci 补全的刊。
    输入说明：原始记录列表、lookup  callable。
    输出说明：JournalKey 列表。
    """
    seen: set[tuple[str | None, str | None]] = set()
    out: list[JournalKey] = []
    for r in records:
        issn = r.get("issn")
        journal = r.get("journal")
        if not journal and not issn:
            continue
        key = (issn, journal)
        if key in seen:
            continue
        if has_metrics_match(lookup(issn, journal)):
            continue
        seen.add(key)
        out.append(JournalKey(issn=issn, journal_title=journal))
    return out


def create_job(
    unknown_keys: list[JournalKey],
    *,
    medsci_enabled: bool = True,
) -> EnrichmentJob | None:
    """创建补全任务（不发起 HTTP）。

    函数功能：注册内存 job。
    输入说明：待补全键列表；medsci_enabled 为 False 时不创建 job。
    输出说明：EnrichmentJob 或 None。
    """
    if not unknown_keys or not medsci_enabled:
        return None
    job_id = str(uuid.uuid4())
    job = EnrichmentJob(job_id=job_id, pending=list(unknown_keys))
    with _jobs_lock:
        _jobs[job_id] = job
    logger.info("创建指标补全任务 %s, pending=%d", job_id, len(unknown_keys))
    return job


def get_job(job_id: str) -> EnrichmentJob | None:
    """按 id 获取任务。"""
    with _jobs_lock:
        return _jobs.get(job_id)


def touch_client(job: EnrichmentJob) -> None:
    """记录客户端最近一次 sync/poll 时间。

    函数功能：更新 last_client_at。
    输入说明：任务对象。
    输出说明：无。
    """
    with job._lock:
        job.last_client_at = time.monotonic()


def client_idle(job: EnrichmentJob, settings: Settings) -> bool:
    """是否超过客户端空闲阈值。

    函数功能：供后台线程判断是否自动取消。
    输入说明：任务、配置。
    输出说明：True 表示应停止补全。
    """
    with job._lock:
        elapsed = time.monotonic() - job.last_client_at
    return elapsed > settings.medsci_client_idle_seconds


def _process_one(
    job: EnrichmentJob,
    key: JournalKey,
    repo: CompositeMetricsRepository,
    settings: Settings,
    last_at: list[float],
) -> EnrichmentUpdate | None:
    """处理单刊并写入 new_metrics。"""
    hit = repo.lookup(key.issn, key.journal_title)
    if has_metrics_match(hit):
        return None
    raw = enrich_one_journal(
        key.issn,
        key.journal_title,
        settings,
        min_interval=settings.medsci_min_interval_seconds,
        last_request_at=last_at,
    )
    if not raw:
        with job._lock:
            job.failed_count += 1
        return None
    row = build_metrics_row_from_medsci(
        journal_name=str(raw["journal_name"]),
        issn=raw.get("issn"),
        impact_factor=raw.get("impact_factor"),
        quartile=str(raw.get("quartile") or "NA"),
        cas_bigclass=raw.get("cas_bigclass"),
    )
    repo.append_entry(row)
    with job._lock:
        job.seq += 1
        seq = job.seq
        upd = EnrichmentUpdate(seq=seq, entry=_public_entry(row))
        job.updates.append(upd)
    return upd


def _public_entry(row: dict[str, Any]) -> dict[str, Any]:
    """返回给前端的条目字段。"""
    return {
        "journal_name": row.get("journal_name"),
        "issn": row.get("issn"),
        "impact_factor": row.get("impact_factor"),
        "quartile": row.get("quartile"),
        "cas_bigclass": row.get("cas_bigclass"),
    }


def _finalize_status(job: EnrichmentJob) -> JobStatus:
    with job._lock:
        if job.cancelled:
            job.status = "cancelled"
        elif job.pending_count == 0:
            job.status = "completed"
        else:
            job.status = "running"
        return job.status


def run_sync_batch(
    job_id: str,
    limit: int | None = None,
    repo: CompositeMetricsRepository | None = None,
    settings: Settings | None = None,
) -> dict[str, Any]:
    """同步处理一批 pending 刊。

    函数功能：最多 limit 本，限速后写入 new_metrics；若仍有 pending 则启后台。
    输入说明：job_id、limit（默认配置 medsci_batch_size）。
    输出说明：API 响应字典。
    """
    settings = settings or get_settings()
    repo = repo or get_metrics_repository()
    job = get_job(job_id)
    if job is None:
        raise KeyError(job_id)
    if job.cancelled:
        raise ValueError("cancelled")
    if job.status == "completed" and job.pending_count == 0:
        raise ValueError("completed")

    touch_client(job)

    cap = limit if limit is not None else settings.medsci_batch_size
    cap = max(1, min(cap, settings.medsci_batch_size))

    batch_entries: list[dict[str, Any]] = []
    sync_count = 0
    last_at = [0.0]

    with job._lock:
        to_run = job.pending[:cap]
        job.pending = job.pending[cap:]

    for key in to_run:
        if job.cancelled:
            break
        upd = _process_one(job, key, repo, settings, last_at)
        if upd:
            batch_entries.append(upd.entry)
            sync_count += 1

    background_started = False
    if job.pending_count > 0 and not job.background_started and not job.cancelled:
        start_background(job_id, repo=repo, settings=settings)
        background_started = True

    status = _finalize_status(job)
    with job._lock:
        seq = job.seq
        pending = job.pending_count
        failed = job.failed_count
        bg = job.background_started

    return {
        "job_id": job_id,
        "status": status,
        "sync_enriched_count": sync_count,
        "pending_count": pending,
        "failed_count": failed,
        "seq": seq,
        "new_entries": batch_entries,
        "background_started": bg or background_started,
    }


def _background_worker(
    job_id: str,
    repo: CompositeMetricsRepository,
    settings: Settings,
) -> None:
    """后台线程：处理剩余 pending。"""
    job = get_job(job_id)
    if job is None:
        return
    with job._lock:
        job.background_running = True
    last_at = [0.0]
    try:
        while True:
            if client_idle(job, settings):
                logger.info("补全任务 %s 客户端空闲超时，自动取消", job_id)
                cancel_job(job_id)
                break
            with job._lock:
                if job.cancelled:
                    break
                if not job.pending:
                    job.status = "completed"
                    break
                key = job.pending.pop(0)
            _process_one(job, key, repo, settings, last_at)
    finally:
        with job._lock:
            job.background_running = False
            if not job.cancelled and job.pending_count == 0:
                job.status = "completed"
    logger.info(
        "补全任务 %s 后台结束 status=%s failed=%d",
        job_id,
        job.status,
        job.failed_count,
    )


def start_background(
    job_id: str,
    repo: CompositeMetricsRepository | None = None,
    settings: Settings | None = None,
) -> None:
    """启动后台补全线程（仅启动一次）。"""
    settings = settings or get_settings()
    repo = repo or get_metrics_repository()
    job = get_job(job_id)
    if job is None:
        return
    with job._lock:
        if job.background_started or job.cancelled:
            return
        job.background_started = True
    thread = threading.Thread(
        target=_background_worker,
        args=(job_id, repo, settings),
        daemon=True,
        name=f"metrics-enrichment-{job_id[:8]}",
    )
    thread.start()


def drain_updates(job_id: str, since_seq: int = 0) -> dict[str, Any]:
    """轮询增量条目。

    函数功能：返回 seq > since_seq 的 new_entries。
    输入说明：job_id、since_seq。
    输出说明：状态与增量列表。
    """
    job = get_job(job_id)
    if job is None:
        raise KeyError(job_id)
    touch_client(job)
    with job._lock:
        entries = [u.entry for u in job.updates if u.seq > since_seq]
        if job.cancelled:
            status: JobStatus = "cancelled"
        elif job.pending_count == 0 and not job.background_running:
            status = "completed"
            job.status = "completed"
        else:
            status = "running"
        seq = job.seq
        pending = job.pending_count
        failed = job.failed_count
    return {
        "job_id": job_id,
        "status": status,
        "pending_count": pending,
        "failed_count": failed,
        "seq": seq,
        "new_entries": entries,
    }


def cancel_job(job_id: str) -> dict[str, Any]:
    """取消任务。"""
    job = get_job(job_id)
    if job is None:
        raise KeyError(job_id)
    with job._lock:
        job.cancelled = True
        job.status = "cancelled"
        job.pending.clear()
        pending = 0
    return {"job_id": job_id, "status": "cancelled", "pending_count": pending}
