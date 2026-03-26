"""PubMed E-utilities：esearch + efetch。"""

import logging
import time
import urllib.parse
from typing import Any

import httpx

from app.config import Settings, get_settings

logger = logging.getLogger(__name__)

ESEARCH_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
EFETCH_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"
EFETCH_BATCH = 200


class PubMedError(Exception):
    """PubMed 请求或解析失败。"""


def _params_base(settings: Settings) -> dict[str, str]:
    """公共查询参数（含可选 api_key）。"""
    p: dict[str, str] = {"db": "pubmed", "tool": "web_demo_pubmed_analyzer"}
    if settings.ncbi_api_key:
        p["api_key"] = settings.ncbi_api_key
    return p


def search_ids(
    query: str,
    max_results: int,
    settings: Settings | None = None,
) -> tuple[list[str], int]:
    """esearch：返回 PMID 列表与命中总数。

    Args:
        query: 检索式。
        max_results: 最多取回的 ID 数。
        settings: 配置。

    Returns:
        (id 列表, 总命中数 count)。

    Raises:
        PubMedError: 网络或非 200。
    """
    settings = settings or get_settings()
    capped = min(max_results, settings.max_analyze_results)
    params = _params_base(settings)
    params.update(
        {
            "term": query,
            "retmax": str(capped),
            "retmode": "json",
            "sort": "relevance",
        },
    )
    url = f"{ESEARCH_URL}?{urllib.parse.urlencode(params)}"
    try:
        with httpx.Client(timeout=settings.http_timeout_seconds) as client:
            r = client.get(url)
    except httpx.HTTPError as e:
        raise PubMedError(f"esearch 网络错误: {e}") from e
    if r.status_code == 429:
        time.sleep(settings.pubmed_retry_sleep_seconds)
        with httpx.Client(timeout=settings.http_timeout_seconds) as client:
            r = client.get(url)
    if r.status_code != 200:
        raise PubMedError(f"esearch HTTP {r.status_code}")
    data = r.json()
    try:
        id_list = data["esearchresult"]["idlist"]
        count_str = data["esearchresult"].get("count", "0")
        total = int(count_str)
    except (KeyError, ValueError) as e:
        raise PubMedError(f"esearch 响应格式异常: {e}") from e
    return id_list, total


def fetch_records_xml(
    ids: list[str],
    settings: Settings | None = None,
) -> str:
    """efetch：按 ID 批量拉取单段 XML（一批内）。"""
    if not ids:
        return '<?xml version="1.0" ?><PubmedArticleSet></PubmedArticleSet>'
    settings = settings or get_settings()
    params = _params_base(settings)
    params.update(
        {
            "id": ",".join(ids),
            "retmode": "xml",
            "rettype": "abstract",
        },
    )
    url = f"{EFETCH_URL}?{urllib.parse.urlencode(params)}"
    with httpx.Client(timeout=settings.http_timeout_seconds) as client:
        try:
            r = client.get(url)
        except httpx.HTTPError as e:
            raise PubMedError(f"efetch 网络错误: {e}") from e
        if r.status_code == 429:
            time.sleep(settings.pubmed_retry_sleep_seconds)
            r = client.get(url)
        if r.status_code != 200:
            raise PubMedError(f"efetch HTTP {r.status_code}")
        return r.text


def search_and_fetch(
    query: str,
    max_results: int,
    settings: Settings | None = None,
) -> tuple[list[dict[str, Any]], int]:
    """检索并解析为记录列表。

    Args:
        query: 检索式。
        max_results: 最大条数。
        settings: 配置。

    Returns:
        (记录字典列表, esearch 报告的总命中数)。
    """
    from app.services.pubmed_parser import parse_efetch_xml

    settings = settings or get_settings()
    ids, total = search_ids(query, max_results, settings)
    records: list[dict[str, Any]] = []
    for i in range(0, len(ids), EFETCH_BATCH):
        batch = ids[i : i + EFETCH_BATCH]
        xml_text = fetch_records_xml(batch, settings)
        records.extend(parse_efetch_xml(xml_text))
        if i + EFETCH_BATCH < len(ids):
            time.sleep(0.12 if not settings.ncbi_api_key else 0.05)
    return records, total
