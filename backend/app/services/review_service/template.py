"""无 LLM 时的结构化中文占位综述。"""

from app.models.schemas import CorpusStats


def template_review(
    stats: CorpusStats,
    abstract_snippets: list[str],
) -> str:
    """无 LLM 时的结构化中文占位综述。"""
    n = stats.analyzed_count
    total = stats.total_hits
    lines = [
        "## 文献概览（模板模式）",
        f"- 检索命中约 **{total}** 条，本次分析纳入 **{n}** 条题录。",
        (
            f"- 期刊指标本地匹配率约 **{stats.journal_match_rate * 100:.1f}%**；"
            "IF/Q 来自本地映射表，非 PubMed 原生字段。"
        ),
    ]
    if stats.year_distribution:
        ys = sorted(stats.year_distribution.keys())[:5]
        lines.append(f"- 年份分布涉及年份示例：{', '.join(ys)} 等。")
    qc = stats.quartile_counts
    if qc:
        parts = [f"{k}: {v}" for k, v in sorted(qc.items())]
        lines.append("- 分区（含未知）计数：" + "；".join(parts) + "。")
    if stats.if_summary.count_matched:
        s = stats.if_summary
        lines.append(
            f"- 已匹配文献的影响因子：均值约 {s.mean or 0:.2f}，"
            f"中位数约 {s.median or 0:.2f}。"
        )
    lines.append("")
    lines.append("### 摘要片段摘录（用于人工综述参考）")
    shown = 0
    for snip in abstract_snippets[:5]:
        clean = (snip or "").strip()
        if len(clean) < 20:
            continue
        short = clean[:400] + ("…" if len(clean) > 400 else "")
        lines.append(f"- {short}")
        shown += 1
        if shown >= 3:
            break
    lines.append("")
    lines.append(
        "> 配置环境变量 `LLM_API_KEY` 与 `LLM_API_BASE` 后，"
        "可生成约 500 字中文分点综述。"
    )
    return "\n".join(lines)
