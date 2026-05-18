"""年分布、分区计数、年份×分区堆积、IF 描述统计、近 5 年 Top100。"""

from __future__ import annotations

import statistics
from datetime import datetime
from typing import Any

from app.models.schemas import ArticleItem, CorpusStats, IfSummary


def _current_year() -> int:
    return datetime.utcnow().year


def _in_last_n_calendar_years(year: int | None, n: int = 5) -> bool:
    """是否落在最近 n 个自然年（含当年），如 n=5 对应 [当年-4, 当年]。"""
    if year is None:
        return False
    cy = _current_year()
    return cy - n < year <= cy


def attach_metrics(
    records: list[dict[str, Any]],
    lookup: Any,
) -> list[ArticleItem]:
    """将原始记录转为 ArticleItem 并 JOIN 指标。"""
    items: list[ArticleItem] = []
    for r in records:
        m = lookup(r.get("issn"), r.get("journal"))
        items.append(
            ArticleItem(
                pmid=str(r["pmid"]),
                title=r.get("title") or "",
                abstract=r.get("abstract"),
                journal=r.get("journal"),
                issn=r.get("issn"),
                year=r.get("year"),
                authors=list(r.get("authors") or []),
                impact_factor=m["impact_factor"] if m else None,
                quartile=m["quartile"] if m else None,
            ),
        )
    return items


def build_corpus_stats(
    articles: list[ArticleItem],
    total_hits: int,
) -> CorpusStats:
    """聚合统计信息。"""
    year_distribution: dict[str, int] = {}
    year_quartile_stacked: dict[str, dict[str, int]] = {}
    quartile_counts: dict[str, int] = {}
    if_values: list[float] = []
    matched = 0
    for a in articles:
        q = a.quartile or "未知"
        if q not in quartile_counts:
            quartile_counts[q] = 0
        quartile_counts[q] += 1
        if a.year is not None:
            yk = str(a.year)
            year_distribution[yk] = year_distribution.get(yk, 0) + 1
            inner = year_quartile_stacked.setdefault(yk, {})
            inner[q] = inner.get(q, 0) + 1
        if a.impact_factor is not None:
            if_values.append(float(a.impact_factor))
            matched += 1
    n = len(articles)
    rate = (matched / n) if n else 0.0
    if_sorted = sorted(if_values)
    median = None
    mean = None
    min_v = None
    max_v = None
    if if_sorted:
        median = float(statistics.median(if_sorted))
        mean = float(statistics.mean(if_sorted))
        min_v = if_sorted[0]
        max_v = if_sorted[-1]
    summary = IfSummary(
        mean=mean,
        median=median,
        if_min=min_v,
        if_max=max_v,
        count_matched=matched,
    )
    def _year_sort_key(k: str) -> tuple[int, str]:
        return (int(k), k) if k.isdigit() else (0, k)

    yq_sorted = {yk: year_quartile_stacked[yk] for yk in sorted(year_quartile_stacked.keys(), key=_year_sort_key)}
    return CorpusStats(
        total_hits=total_hits,
        analyzed_count=n,
        journal_match_rate=round(rate, 4),
        year_distribution=dict(sorted(year_distribution.items(), key=lambda kv: _year_sort_key(kv[0]))),
        quartile_counts=quartile_counts,
        year_quartile_stacked=yq_sorted,
        if_summary=summary,
    )


def top100_if_recent_years(
    articles: list[ArticleItem],
    years: int = 5,
) -> list[ArticleItem]:
    """近若干自然年文献按 IF 降序取前 100；无 IF 置底（按年份再按标题）。"""
    recent = [a for a in articles if _in_last_n_calendar_years(a.year, years)]

    def sort_key(a: ArticleItem) -> tuple[int, float, int, str]:
        has_if = 1 if a.impact_factor is not None else 0
        if_val = float(a.impact_factor) if a.impact_factor is not None else -1.0
        y = a.year or 0
        return (has_if, if_val, y, a.title)

    ranked = sorted(recent, key=sort_key, reverse=True)
    return ranked[:100]
