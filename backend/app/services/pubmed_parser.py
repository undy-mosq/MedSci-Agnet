"""将 PubMed efetch XML 解析为结构化记录（无 HTTP，便于单测）。"""

import logging
import re
import xml.etree.ElementTree as ET
from typing import Any

logger = logging.getLogger(__name__)


def _local_tag(tag: str) -> str:
    """去掉 XML 命名空间前缀。"""
    if "}" in tag:
        return tag.split("}", 1)[1]
    return tag


def _text(el: ET.Element | None) -> str:
    """取元素内全部文本。"""
    if el is None:
        return ""
    parts: list[str] = []
    if el.text:
        parts.append(el.text)
    for child in el:
        parts.append(_text(child))
        if child.tail:
            parts.append(child.tail)
    return "".join(parts).strip()


def _find_first(parent: ET.Element, *names: str) -> ET.Element | None:
    """按本地标签名深度优先查找第一个匹配节点。"""
    if _local_tag(parent.tag) in names:
        return parent
    for child in parent:
        found = _find_first(child, *names)
        if found is not None:
            return found
    return None


def _collect_authors(article_el: ET.Element) -> list[str]:
    """解析作者列表（LastName + Initials）。"""
    names: list[str] = []
    for auth in article_el.iter():
        if _local_tag(auth.tag) != "Author":
            continue
        last = None
        fore = None
        for ch in auth:
            t = _local_tag(ch.tag)
            if t == "LastName":
                last = (ch.text or "").strip()
            elif t == "ForeName":
                fore = (ch.text or "").strip()
            elif t == "Initials" and fore is None:
                fore = (ch.text or "").strip()
        if last:
            if fore:
                names.append(f"{last} {fore}")
            else:
                names.append(last)
    return names[:50]


def _parse_year(medline_or_article: ET.Element) -> int | None:
    """从 MedlineCitation / Article 子树解析年份。"""
    for el in medline_or_article.iter():
        if _local_tag(el.tag) == "Year" and el.text and el.text.strip().isdigit():
            y = int(el.text.strip())
            if 1800 <= y <= 2100:
                return y
        if _local_tag(el.tag) == "MedlineDate":
            m = re.search(r"(19|20)\d{2}", _text(el) or "")
            if m:
                return int(m.group(0))
    return None


def _parse_issn(journal_el: ET.Element) -> str | None:
    """取 Print 或 Electronic ISSN。"""
    preferred: list[tuple[str, str]] = []
    for issn in journal_el.iter():
        if _local_tag(issn.tag) != "ISSN":
            continue
        typ = (issn.get("IssnType") or "").lower()
        val = (issn.text or "").strip()
        if not val:
            continue
        preferred.append((typ, val))
    for typ in ("print", "electronic", "linking"):
        for t, v in preferred:
            if t == typ:
                return v
    if preferred:
        return preferred[0][1]
    return None


def _parse_journal_title(journal_el: ET.Element) -> str | None:
    """期刊名 ISOAbbreviation 或 Title。"""
    for tag_name in ("ISOAbbreviation", "Title"):
        for el in journal_el.iter():
            if _local_tag(el.tag) == tag_name and el.text:
                return el.text.strip()
    return None


def parse_efetch_xml(xml_text: str) -> list[dict[str, Any]]:
    """解析 efetch 返回的 PubMed XML。

    Args:
        xml_text: NCBI 返回的 XML 字符串。

    Returns:
        字典列表，键含 pmid, title, abstract, journal, issn, year, authors。
    """
    root = ET.fromstring(xml_text)
    out: list[dict[str, Any]] = []
    for pub_article in root.iter():
        if _local_tag(pub_article.tag) != "PubmedArticle":
            continue
        medline = _find_first(pub_article, "MedlineCitation")
        article_el = _find_first(pub_article, "Article")
        if medline is None or article_el is None:
            continue
        pmid_el = _find_first(medline, "PMID")
        pmid = (pmid_el.text or "").strip() if pmid_el is not None else ""
        title_el = _find_first(article_el, "ArticleTitle")
        title = _text(title_el)
        abstract_el = _find_first(article_el, "Abstract")
        abstract_parts: list[str] = []
        if abstract_el is not None:
            for ab in abstract_el:
                if _local_tag(ab.tag) == "AbstractText":
                    label = ab.get("Label")
                    chunk = _text(ab)
                    if label:
                        chunk = f"{label}: {chunk}"
                    if chunk:
                        abstract_parts.append(chunk)
        abstract = "\n".join(abstract_parts) if abstract_parts else None
        journal_el = _find_first(article_el, "Journal")
        journal = None
        issn = None
        year = _parse_year(medline) or _parse_year(article_el)
        if journal_el is not None:
            journal = _parse_journal_title(journal_el)
            issn = _parse_issn(journal_el)
            if year is None:
                ji = _find_first(journal_el, "JournalIssue")
                if ji is not None:
                    year = _parse_year(ji)
        authors = _collect_authors(article_el)
        if not pmid:
            logger.warning("跳过无 PMID 条目")
            continue
        out.append(
            {
                "pmid": pmid,
                "title": title or "(no title)",
                "abstract": abstract,
                "journal": journal,
                "issn": issn,
                "year": year,
                "authors": authors,
            },
        )
    return out
