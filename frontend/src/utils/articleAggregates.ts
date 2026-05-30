/** [2026-05-18] 从 articles 本地聚合期刊 Top、IF 直方图、摘要覆盖率。 */
/** [2026-05-19] 新增 journalDetailForName 供期刊图点击展示指标。 */
/** [2026-05-19] ifHistogram 返回含空桶与 step/域边界，供数值轴直方图。 */

import type { ArticleItem } from '@/api/analyze';

export interface JournalCount {
  name: string;
  count: number;
}

export interface JournalDetail {
  name: string;
  count: number;
  issn: string | null;
  impact_factor: number | null;
  quartile: string | null;
}

export interface IfBin {
  range: string;
  min: number;
  max: number;
  count: number;
}

export interface IfHistogramResult {
  bins: IfBin[];
  step: number;
  domainMin: number;
  domainMax: number;
}

export interface AbstractCoverage {
  withAbstract: number;
  total: number;
  rate: number;
}

/** 函数功能：统计摘要非空篇数与占比。
 *  输入说明：articles 为文献列表。
 *  输出说明：withAbstract、total、rate（0–1）。 */
export function abstractCoverage(articles: ArticleItem[]): AbstractCoverage {
  const total = articles.length;
  let withAbstract = 0;
  for (const a of articles) {
    if (a.abstract?.trim()) {
      withAbstract += 1;
    }
  }
  return {
    withAbstract,
    total,
    rate: total ? withAbstract / total : 0,
  };
}

/** 函数功能：按期刊名计数并取 Top N。
 *  输入说明：articles、n 为条数上限。
 *  输出说明：按 count 降序的 { name, count }[]。 */
export function topJournals(articles: ArticleItem[], n = 12): JournalCount[] {
  const map = new Map<string, number>();
  for (const a of articles) {
    const name = a.journal?.trim() || '（未知期刊）';
    map.set(name, (map.get(name) ?? 0) + 1);
  }
  return [...map.entries()]
    .map(([name, count]) => ({ name, count }))
    .sort((a, b) => b.count - a.count || a.name.localeCompare(b.name))
    .slice(0, n);
}

/** 函数功能：按期刊名聚合单刊指标（与 topJournals 命名规则一致）。
 *  输入说明：articles 文献列表；name 为期刊名（含「（未知期刊）」）。
 *  输出说明：篇数及首条有效 ISSN/IF/分区，无匹配返回 null。 */
export function journalDetailForName(
  articles: ArticleItem[],
  name: string,
): JournalDetail | null {
  const rows = articles.filter((a) => {
    const j = a.journal?.trim() || '（未知期刊）';
    return j === name;
  });
  if (!rows.length) {
    return null;
  }
  let issn: string | null = null;
  let impact_factor: number | null = null;
  let quartile: string | null = null;
  for (const a of rows) {
    if (!issn && a.issn?.trim()) {
      issn = a.issn.trim();
    }
    if (impact_factor == null && a.impact_factor != null && Number.isFinite(a.impact_factor)) {
      impact_factor = a.impact_factor;
    }
    if (!quartile && a.quartile?.trim()) {
      quartile = a.quartile.trim();
    }
    if (issn && impact_factor != null && quartile) {
      break;
    }
  }
  return {
    name,
    count: rows.length,
    issn,
    impact_factor,
    quartile,
  };
}

/** 函数功能：将影响因子分桶为直方图区间（保留空桶）。
 *  输入说明：articles、binCount 为桶数（默认 8）。
 *  输出说明：bins、step、domainMin/domainMax；无有效 IF 时返回 null。 */
export function ifHistogram(
  articles: ArticleItem[],
  binCount = 8,
): IfHistogramResult | null {
  const values = articles
    .map((a) => a.impact_factor)
    .filter((v): v is number => v != null && Number.isFinite(v));
  if (!values.length) {
    return null;
  }
  const min = Math.min(...values);
  const max = Math.max(...values);
  if (min === max) {
    const pad = Math.max(min * 0.05, 0.5);
    return {
      bins: [
        {
          range: `${min.toFixed(1)}`,
          min,
          max,
          count: values.length,
        },
      ],
      step: 0,
      domainMin: min - pad,
      domainMax: max + pad,
    };
  }
  const step = (max - min) / binCount;
  const bins: IfBin[] = [];
  for (let i = 0; i < binCount; i++) {
    const lo = min + i * step;
    const hi = i === binCount - 1 ? max : min + (i + 1) * step;
    const label =
      i === binCount - 1
        ? `${lo.toFixed(1)}–${hi.toFixed(1)}`
        : `${lo.toFixed(1)}–${(min + (i + 1) * step).toFixed(1)}`;
    bins.push({ range: label, min: lo, max: hi, count: 0 });
  }
  for (const v of values) {
    let idx = Math.floor((v - min) / step);
    if (idx >= binCount) {
      idx = binCount - 1;
    }
    bins[idx]!.count += 1;
  }
  return {
    bins,
    step,
    domainMin: min,
    domainMax: max,
  };
}
