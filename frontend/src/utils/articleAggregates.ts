/** [2026-05-18] 从 articles 本地聚合期刊 Top、IF 直方图、摘要覆盖率。 */

import type { ArticleItem } from '@/api/analyze';

export interface JournalCount {
  name: string;
  count: number;
}

export interface IfBin {
  range: string;
  min: number;
  max: number;
  count: number;
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

/** 函数功能：将影响因子分桶为直方图区间。
 *  输入说明：articles、binCount 为桶数（默认 8）。
 *  输出说明：每桶 range 标签、min/max、count。 */
export function ifHistogram(articles: ArticleItem[], binCount = 8): IfBin[] {
  const values = articles
    .map((a) => a.impact_factor)
    .filter((v): v is number => v != null && Number.isFinite(v));
  if (!values.length) {
    return [];
  }
  const min = Math.min(...values);
  const max = Math.max(...values);
  if (min === max) {
    return [
      {
        range: `${min.toFixed(1)}`,
        min,
        max,
        count: values.length,
      },
    ];
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
  return bins.filter((b) => b.count > 0);
}
