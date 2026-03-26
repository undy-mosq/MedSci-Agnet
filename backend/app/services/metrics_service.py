"""期刊影响因子与分区：本地 JSON 映射查询。"""

import json
import logging
import re
from pathlib import Path
from typing import Any

from app.config import Settings, get_settings

logger = logging.getLogger(__name__)


def _normalize_issn(raw: str | None) -> str | None:
    """去掉 ISSN 中的连字符并转小写。"""
    if not raw:
        return None
    s = re.sub(r"[^0-9Xx]", "", raw.strip())
    return s.lower() or None


def _normalize_title(title: str | None) -> str:
    """刊名规范化用于模糊匹配。"""
    if not title:
        return ""
    t = title.lower()
    t = re.sub(r"[^a-z0-9]+", " ", t)
    return " ".join(t.split())


class JournalMetricsRepository:
    """加载并查询期刊指标。"""

    def __init__(self, path: Path | None = None, settings: Settings | None = None) -> None:
        """Args:
            path: JSON 文件路径；默认来自配置。
            settings: 应用配置。
        """
        self._settings = settings or get_settings()
        self._path = path or self._settings.journal_metrics_path
        self._by_issn: dict[str, dict[str, Any]] = {}
        self._by_title: dict[str, dict[str, Any]] = {}
        self._loaded = False

    def load(self) -> None:
        """从磁盘加载映射表。"""
        if self._loaded:
            return
        p = self._path
        if not p.is_file():
            logger.warning("期刊指标文件不存在: %s", p)
            self._loaded = True
            return
        with open(p, encoding="utf-8") as f:
            data = json.load(f)
        if isinstance(data, dict) and "journals" in data:
            rows = data["journals"]
        else:
            rows = data
        for row in rows:
            if not isinstance(row, dict):
                continue
            issn = _normalize_issn(row.get("issn"))
            name = row.get("journal_name") or row.get("name") or ""
            entry = {
                "impact_factor": float(row["impact_factor"])
                if row.get("impact_factor") is not None
                else None,
                "quartile": str(row.get("quartile") or "NA"),
                "journal_name": str(name),
            }
            if issn:
                self._by_issn[issn] = entry
            nt = _normalize_title(str(name))
            if nt:
                self._by_title[nt] = entry
        self._loaded = True
        logger.info(
            "期刊指标已加载: issn=%d, title=%d",
            len(self._by_issn),
            len(self._by_title),
        )

    def lookup(self, issn: str | None, journal_title: str | None) -> dict[str, Any] | None:
        """按 ISSN 优先、其次规范化刊名匹配。

        Returns:
            含 impact_factor, quartile, journal_name；未匹配返回 None。
        """
        self.load()
        ni = _normalize_issn(issn)
        if ni and ni in self._by_issn:
            return dict(self._by_issn[ni])
        nt = _normalize_title(journal_title)
        if nt and nt in self._by_title:
            return dict(self._by_title[nt])
        # 子串弱匹配（Demo 用）
        if nt:
            for key, val in self._by_title.items():
                if key in nt or nt in key:
                    return dict(val)
        return None


_repo: JournalMetricsRepository | None = None


def get_metrics_repository() -> JournalMetricsRepository:
    """单例仓库。"""
    global _repo
    if _repo is None:
        _repo = JournalMetricsRepository()
    return _repo
