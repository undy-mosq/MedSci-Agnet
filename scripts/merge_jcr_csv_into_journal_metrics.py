"""将 JCR CSV（刊名、IF、分区）合并进 data/journal_metrics.json。

分区「1区」–「4区」映射为 Q1–Q4；刊名规范化规则与 app.services.metrics_service 一致。
"""

from __future__ import annotations

import csv
import json
import re
from pathlib import Path


def normalize_title(title: str | None) -> str:
    """刊名规范化用于匹配。"""
    if not title:
        return ""
    t = title.lower()
    t = re.sub(r"[^a-z0-9]+", " ", t)
    return " ".join(t.split())


def jcr_zone_to_quartile(zone: str) -> str:
    """CSV 中的「1区」等转为 Q1–Q4。"""
    z = (zone or "").strip()
    if z.startswith("1"):
        return "Q1"
    if z.startswith("2"):
        return "Q2"
    if z.startswith("3"):
        return "Q3"
    if z.startswith("4"):
        return "Q4"
    return "NA"


def load_csv_rows(csv_path: Path) -> list[tuple[str, float, str]]:
    """返回 (刊名, IF, quartile Q1–Q4)。同一规范化刊名后者覆盖前者。"""
    out: dict[str, tuple[str, float, str]] = {}
    with open(csv_path, encoding="utf-8-sig", newline="") as f:
        reader = csv.reader(f)
        header = next(reader, None)
        if not header:
            return []
        for row in reader:
            if len(row) < 3:
                continue
            name = row[0].strip()
            if not name:
                continue
            try:
                if_val = float(str(row[1]).strip())
            except ValueError:
                continue
            q = jcr_zone_to_quartile(row[2])
            nk = normalize_title(name)
            if not nk:
                continue
            out[nk] = (name, if_val, q)
    return list(out.values())


def merge(csv_path: Path, json_path: Path) -> tuple[int, int, int]:
    """合并 CSV 到 JSON。返回 (更新条数, 新增条数, JSON 合并后总条数)。"""
    csv_rows = load_csv_rows(csv_path)
    csv_by_norm: dict[str, tuple[str, float, str]] = {}
    for name, if_val, q in csv_rows:
        nk = normalize_title(name)
        csv_by_norm[nk] = (name, if_val, q)

    with open(json_path, encoding="utf-8") as f:
        data = json.load(f)
    if isinstance(data, dict) and "journals" in data:
        rows = data["journals"]
        wrapped = True
    else:
        rows = data
        wrapped = False

    if not isinstance(rows, list):
        raise ValueError("journal_metrics.json 应为数组或含 journals 数组的对象")

    existing_norms: set[str] = set()
    for entry in rows:
        if not isinstance(entry, dict):
            continue
        name = entry.get("journal_name") or entry.get("name") or ""
        nt = normalize_title(str(name))
        if nt:
            existing_norms.add(nt)

    updated = 0
    for entry in rows:
        if not isinstance(entry, dict):
            continue
        name = entry.get("journal_name") or entry.get("name") or ""
        nt = normalize_title(str(name))
        if nt not in csv_by_norm:
            continue
        src_name, if_val, q = csv_by_norm[nt]
        entry["journal_name"] = entry.get("journal_name") or src_name
        entry["impact_factor"] = if_val
        entry["quartile"] = q
        updated += 1

    added = 0
    for nk, (src_name, if_val, q) in csv_by_norm.items():
        if nk in existing_norms:
            continue
        rows.append(
            {
                "journal_name": src_name,
                "impact_factor": if_val,
                "quartile": q,
            }
        )
        added += 1

    def sort_key(e: dict) -> float:
        v = e.get("impact_factor")
        try:
            return float(v) if v is not None else float("-inf")
        except (TypeError, ValueError):
            return float("-inf")

    rows.sort(key=sort_key, reverse=True)

    out_data = {"journals": rows} if wrapped else rows
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(out_data, f, ensure_ascii=False, indent=2)
        f.write("\n")

    return updated, added, len(rows)


if __name__ == "__main__":
    root = Path(__file__).resolve().parents[1]
    csv_p = Path(r"d:\新建文件夹\Python\pythonProject\LLMProject\Test\jcr_2.csv")
    json_p = root / "data" / "journal_metrics.json"
    u, a, n = merge(csv_p, json_p)
    print(f"更新: {u}, 新增: {a}, 合并后总条数: {n}")
