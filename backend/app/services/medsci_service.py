"""[2026-05-19] MedSci 期刊 IF 与中科院大类分区抓取（HTML 解析）。"""

from __future__ import annotations

import logging
import re
import time
import urllib.parse
from dataclasses import dataclass
from typing import Any

import httpx

from app.config import Settings, get_settings
from app.services.metrics_service import normalize_issn, normalize_title

logger = logging.getLogger(__name__)

MEDSCI_INDEX_URL = "https://www.medsci.cn/sci/index.do"
MEDSCI_JOURNAL_URL = "https://www.medsci.cn/sci/journal.do"

USER_AGENT = (
    "Mozilla/5.0 (compatible; web_demo_pubmed_analyzer/1.0; +https://example.local)"
)


class MedSciError(Exception):
    """MedSci 请求或解析失败。"""


@dataclass
class MedSciCandidate:
    """搜索候选刊。"""

    journal_id: str
    fullname: str
    abbr: str | None
    issn: str | None
    impact_factor: float | None


@dataclass
class MedSciDetail:
    """期刊详情。"""

    journal_id: str
    fullname: str
    issn: str | None
    impact_factor: float | None
    cas_bigclass: str | None
    quartile: str


def cas_bigclass_to_quartile(cas_bigclass: str | None) -> str:
    """中科院大类字符串转 Q1–Q4。

    函数功能：从「医学 2区」等提取区号。
    输入说明：bigclassCas 原文。
    输出说明：Q1–Q4 或 NA。
    """
    if not cas_bigclass:
        return "NA"
    m = re.search(r"(\d)\s*区", cas_bigclass)
    if not m:
        return "NA"
    return f"Q{m.group(1)}"


def _parse_float(raw: str | None) -> float | None:
    if raw is None:
        return None
    s = raw.strip()
    if not s or s in ("null", "暂无数据"):
        return None
    try:
        return float(s)
    except ValueError:
        return None


def _fetch_html(url: str, settings: Settings) -> str:
    """GET 页面 HTML。"""
    headers = {"User-Agent": USER_AGENT, "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8"}
    try:
        with httpx.Client(
            timeout=settings.http_timeout_seconds,
            follow_redirects=True,
        ) as client:
            resp = client.get(url, headers=headers)
            resp.raise_for_status()
            return resp.text
    except httpx.HTTPError as e:
        raise MedSciError(f"MedSci 请求失败: {e}") from e


def _parse_list_responses(html: str) -> list[MedSciCandidate]:
    """解析列表页内嵌 GetPortalToolImpactFactorPageResponse。"""
    pattern = re.compile(
        r"GetPortalToolImpactFactorPageResponse\("
        r"id=([^,]+),\s*projectId=\d+,\s*cover=[^,]*,\s*"
        r"name=([^,]*),\s*abbr=([^,]*),\s*fullname=([^,]+),"
        r"[^)]*?impactFactor=([^,]+),\s*articleNumbers=[^,]*,\s*"
        r"acceptanceRate=[^,]*,\s*issn=([^,\s]+)",
        re.DOTALL,
    )
    out: list[MedSciCandidate] = []
    for m in pattern.finditer(html):
        jid = m.group(1).strip()
        fullname = m.group(4).strip()
        issn_raw = m.group(6).strip()
        if not jid or not fullname:
            continue
        out.append(
            MedSciCandidate(
                journal_id=jid,
                fullname=fullname,
                abbr=m.group(3).strip() or None,
                issn=issn_raw if issn_raw and issn_raw != "null" else None,
                impact_factor=_parse_float(m.group(5)),
            ),
        )
    return out


def _pick_candidate(
    candidates: list[MedSciCandidate],
    issn: str | None,
    journal_title: str | None,
) -> MedSciCandidate | None:
    """ISSN / 刊名消歧选一条。"""
    if not candidates:
        return None
    ni = normalize_issn(issn)
    if ni:
        for c in candidates:
            if normalize_issn(c.issn) == ni:
                return c
    nt = normalize_title(journal_title)
    if nt:
        exact = [c for c in candidates if normalize_title(c.fullname) == nt]
        if len(exact) == 1:
            return exact[0]
        if exact:
            with_if = [c for c in exact if c.impact_factor is not None]
            return with_if[0] if with_if else exact[0]
        partial = [
            c
            for c in candidates
            if nt in normalize_title(c.fullname)
            or normalize_title(c.fullname) in nt
        ]
        if len(partial) == 1:
            return partial[0]
        if partial:
            with_if = [c for c in partial if c.impact_factor is not None]
            return with_if[0] if with_if else partial[0]
    with_if = [c for c in candidates if c.impact_factor is not None]
    return with_if[0] if with_if else candidates[0]


def search_journal_candidates(
    journal_title: str | None,
    issn: str | None,
    settings: Settings | None = None,
) -> list[MedSciCandidate]:
    """MedSci 列表搜索。

    函数功能：按刊名检索候选。
    输入说明：刊名、ISSN（用于后续消歧）。
    输出说明：候选列表。
    """
    settings = settings or get_settings()
    q = (journal_title or issn or "").strip()
    if not q:
        return []
    params = urllib.parse.urlencode(
        {"fullname": q, "page": "1", "type": "sci", "source": "1", "is_highlight": "0"},
    )
    url = f"{MEDSCI_INDEX_URL}?{params}"
    html = _fetch_html(url, settings)
    return _parse_list_responses(html)


def fetch_journal_detail(
    journal_id: str,
    settings: Settings | None = None,
) -> MedSciDetail:
    """MedSci 期刊详情页。

    函数功能：取 IF 与中科院大类。
    输入说明：MedSci 内部 id。
    输出说明：MedSciDetail。
    """
    settings = settings or get_settings()
    url = f"{MEDSCI_JOURNAL_URL}?id={urllib.parse.quote(journal_id)}"
    html = _fetch_html(url, settings)
    fullname_m = re.search(r"fullname=([^,]+),", html)
    if_m = re.search(r"impactFactor=([^,]+),", html)
    issn_m = re.search(r"issn=([^,]+),", html)
    cas_m = re.search(r"bigclassCas=([^,]+),", html)
    fullname = fullname_m.group(1).strip() if fullname_m else ""
    issn_raw = issn_m.group(1).strip() if issn_m else None
    issn = issn_raw if issn_raw and issn_raw != "null" else None
    cas_bigclass = cas_m.group(1).strip() if cas_m else None
    if cas_bigclass in ("null", "暂无数据"):
        cas_bigclass = None
    impact_factor = _parse_float(if_m.group(1) if if_m else None)
    quartile = cas_bigclass_to_quartile(cas_bigclass)
    return MedSciDetail(
        journal_id=journal_id,
        fullname=fullname or journal_id,
        issn=issn,
        impact_factor=impact_factor,
        cas_bigclass=cas_bigclass,
        quartile=quartile,
    )


def enrich_one_journal(
    issn: str | None,
    journal_title: str | None,
    settings: Settings | None = None,
    *,
    min_interval: float = 0.0,
    last_request_at: list[float] | None = None,
) -> dict[str, Any] | None:
    """搜索 + 详情，返回可写入 new_metrics 的字段 dict。

    函数功能：对单刊执行 MedSci 补全。
    输入说明：ISSN、刊名、配置；可选限速状态 last_request_at。
    输出说明：成功时含 journal_name/issn/impact_factor/quartile/cas_bigclass；失败 None。
    """
    settings = settings or get_settings()
    if last_request_at is not None and min_interval > 0:
        elapsed = time.monotonic() - last_request_at[0]
        if elapsed < min_interval:
            time.sleep(min_interval - elapsed)
    try:
        candidates = search_journal_candidates(journal_title, issn, settings)
        if last_request_at is not None:
            last_request_at[0] = time.monotonic()
        pick = _pick_candidate(candidates, issn, journal_title)
        if not pick:
            return None
        detail = fetch_journal_detail(pick.journal_id, settings)
        if last_request_at is not None:
            last_request_at[0] = time.monotonic()
        name = detail.fullname or journal_title or ""
        return {
            "journal_name": name,
            "issn": detail.issn or issn,
            "impact_factor": detail.impact_factor,
            "quartile": detail.quartile,
            "cas_bigclass": detail.cas_bigclass,
        }
    except MedSciError as e:
        logger.warning(
            "MedSci 补全失败 journal=%s issn=%s: %s",
            journal_title,
            issn,
            e,
        )
        return None
