"""[2026-05-19] 期刊指标：主表 + new_metrics 复合 lookup；new 表可追加写入。"""

from __future__ import annotations

import json
import logging
import re
import tempfile
import threading
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from app.config import Settings, get_settings

logger = logging.getLogger(__name__)

_write_lock = threading.Lock()


def normalize_issn(raw: str | None) -> str | None:
    """ISSN 规范化。

    函数功能：去掉连字符并转小写。
    输入说明：原始 ISSN 字符串。
    输出说明：规范化 ISSN 或 None。
    """
    if not raw:
        return None
    s = re.sub(r"[^0-9Xx]", "", raw.strip())
    return s.lower() or None


def normalize_title(title: str | None) -> str:
    """刊名规范化。

    函数功能：小写并保留字母数字用于匹配。
    输入说明：期刊标题。
    输出说明：规范化刊名键。
    """
    if not title:
        return ""
    t = title.lower()
    t = re.sub(r"[^a-z0-9]+", " ", t)
    return " ".join(t.split())


def _parse_rows_from_file(path: Path) -> list[dict[str, Any]]:
    """从 JSON 文件读取期刊行列表。"""
    if not path.is_file():
        return []
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    if isinstance(data, dict) and "journals" in data:
        rows = data["journals"]
    else:
        rows = data
    if not isinstance(rows, list):
        return []
    return [r for r in rows if isinstance(r, dict)]


def _row_to_entry(row: dict[str, Any]) -> dict[str, Any]:
    """将 JSON 行转为 lookup 条目。"""
    name = row.get("journal_name") or row.get("name") or ""
    entry: dict[str, Any] = {
        "impact_factor": float(row["impact_factor"])
        if row.get("impact_factor") is not None
        else None,
        "quartile": str(row.get("quartile") or "NA"),
        "journal_name": str(name),
    }
    if row.get("cas_bigclass"):
        entry["cas_bigclass"] = str(row["cas_bigclass"])
    return entry


def _load_rows_into_indexes(
    rows: list[dict[str, Any]],
    by_issn: dict[str, dict[str, Any]],
    by_title: dict[str, dict[str, Any]],
    *,
    fuzzy_title: bool,
) -> None:
    """将行列表写入 ISSN / 刊名索引。

    函数功能：构建内存索引供 lookup 使用。
    输入说明：rows、目标 dict、fuzzy_title 是否启用子串弱匹配索引。
    输出说明：无，就地修改 by_issn / by_title。
    """
    for row in rows:
        issn = normalize_issn(row.get("issn"))
        name = row.get("journal_name") or row.get("name") or ""
        entry = _row_to_entry(row)
        if issn:
            by_issn[issn] = entry
        nt = normalize_title(str(name))
        if nt:
            by_title[nt] = entry


class _MetricsIndex:
    """单文件指标索引。"""

    def __init__(self, *, fuzzy_title: bool) -> None:
        self._by_issn: dict[str, dict[str, Any]] = {}
        self._by_title: dict[str, dict[str, Any]] = {}
        self._fuzzy_title = fuzzy_title
        self._loaded = False

    def load_from_path(self, path: Path) -> None:
        """从路径加载。"""
        rows = _parse_rows_from_file(path)
        _load_rows_into_indexes(
            rows,
            self._by_issn,
            self._by_title,
            fuzzy_title=self._fuzzy_title,
        )
        self._loaded = True

    def lookup(self, issn: str | None, journal_title: str | None) -> dict[str, Any] | None:
        """按 ISSN / 刊名查询。"""
        ni = normalize_issn(issn)
        if ni and ni in self._by_issn:
            return dict(self._by_issn[ni])
        nt = normalize_title(journal_title)
        if nt and nt in self._by_title:
            return dict(self._by_title[nt])
        if self._fuzzy_title and nt:
            for key, val in self._by_title.items():
                if key in nt or nt in key:
                    return dict(val)
        return None

    def apply_entry(self, row: dict[str, Any]) -> None:
        """将单条写入内存索引（不写盘）。"""
        _load_rows_into_indexes(
            [row],
            self._by_issn,
            self._by_title,
            fuzzy_title=self._fuzzy_title,
        )


class JournalMetricsRepository:
    """只读主表 journal_metrics.json。"""

    def __init__(self, path: Path | None = None, settings: Settings | None = None) -> None:
        self._settings = settings or get_settings()
        self._path = path or self._settings.journal_metrics_path
        self._index = _MetricsIndex(fuzzy_title=True)

    def load(self) -> None:
        """加载主表。"""
        if self._index._loaded:
            return
        p = self._path
        if not p.is_file():
            logger.warning("期刊指标文件不存在: %s", p)
            self._index._loaded = True
            return
        self._index.load_from_path(p)
        logger.info(
            "主表期刊指标已加载: 刊名=%d, ISSN=%d",
            len(self._index._by_title),
            len(self._index._by_issn),
        )

    def lookup(self, issn: str | None, journal_title: str | None) -> dict[str, Any] | None:
        """查询主表。"""
        self.load()
        return self._index.lookup(issn, journal_title)


class CompositeMetricsRepository:
    """主表 + new_metrics 复合查询；可向 new_metrics 追加。"""

    def __init__(self, settings: Settings | None = None) -> None:
        self._settings = settings or get_settings()
        self._primary = JournalMetricsRepository(settings=self._settings)
        self._new_path = self._settings.new_journal_metrics_path
        self._new_index = _MetricsIndex(fuzzy_title=False)
        self._new_loaded = False

    def _load_new(self) -> None:
        if self._new_loaded:
            return
        if not self._new_path.is_file():
            self._new_path.parent.mkdir(parents=True, exist_ok=True)
            self._new_path.write_text("[]\n", encoding="utf-8")
        self._new_index.load_from_path(self._new_path)
        self._new_loaded = True
        logger.info(
            "new_metrics 已加载: 刊名=%d, ISSN=%d",
            len(self._new_index._by_title),
            len(self._new_index._by_issn),
        )

    def reload_new_metrics(self) -> None:
        """重新从磁盘加载 new_metrics。"""
        self._new_index = _MetricsIndex(fuzzy_title=False)
        self._new_loaded = False
        self._load_new()

    def lookup(self, issn: str | None, journal_title: str | None) -> dict[str, Any] | None:
        """先主表（含弱匹配），再 new_metrics（精确）。"""
        hit = self._primary.lookup(issn, journal_title)
        if hit:
            return hit
        self._load_new()
        return self._new_index.lookup(issn, journal_title)

    def append_entry(self, row: dict[str, Any]) -> None:
        """线程安全追加一条到 new_metrics.json 并更新内存索引。

        函数功能：读-改-写 JSON 数组。
        输入说明：含 journal_name、issn、impact_factor、quartile 等字段的字典。
        输出说明：无。
        """
        with _write_lock:
            rows = _parse_rows_from_file(self._new_path)
            rows.append(row)
            payload: list[dict[str, Any]] | dict[str, Any] = rows
            parent = self._new_path.parent
            parent.mkdir(parents=True, exist_ok=True)
            with tempfile.NamedTemporaryFile(
                mode="w",
                encoding="utf-8",
                dir=parent,
                delete=False,
                suffix=".tmp",
            ) as tmp:
                json.dump(payload, tmp, ensure_ascii=False, indent=2)
                tmp.write("\n")
                tmp_path = Path(tmp.name)
            tmp_path.replace(self._new_path)
        self._new_index.apply_entry(row)

    @property
    def new_metrics_path(self) -> Path:
        return self._new_path


_repo: CompositeMetricsRepository | None = None


def get_metrics_repository() -> CompositeMetricsRepository:
    """复合指标仓库单例。"""
    global _repo
    if _repo is None:
        _repo = CompositeMetricsRepository()
    return _repo


def has_metrics_match(entry: dict[str, Any] | None) -> bool:
    """是否视为已匹配到 IF 或分区。

    函数功能：判断 lookup 结果是否含有效指标。
    输入说明：lookup 返回值。
    输出说明：有 impact_factor 或非空 quartile（且非 NA）时为 True。
    """
    if not entry:
        return False
    if entry.get("impact_factor") is not None:
        return True
    q = entry.get("quartile")
    return bool(q and str(q).upper() not in ("NA", "N/A", "未知"))


def build_metrics_row_from_medsci(
    *,
    journal_name: str,
    issn: str | None,
    impact_factor: float | None,
    quartile: str,
    cas_bigclass: str | None,
) -> dict[str, Any]:
    """构造写入 new_metrics 的行。"""
    row: dict[str, Any] = {
        "journal_name": journal_name,
        "impact_factor": impact_factor,
        "quartile": quartile,
        "source": "medsci",
        "fetched_at": datetime.now(timezone.utc).isoformat(),
    }
    if issn:
        row["issn"] = issn
    if cas_bigclass:
        row["cas_bigclass"] = cas_bigclass
    return row
