/** [2026-05-19] 语料统计；NA 在统计中并入「未知」。 */

import type { ArticleItem, CorpusStats, IfSummary } from '@/api/analyze';
import { quartileGroupKey } from '@/utils/quartileDisplay';

function currentUtcYear(): number {
  return new Date().getUTCFullYear();
}

/** 与 Python `_in_last_n_calendar_years` 一致：近 n 个自然年（含当年）。 */
export function inLastNYears(year: number | null, n: number): boolean {
  if (year == null) return false;
  const cy = currentUtcYear();
  return cy - n < year && year <= cy;
}

export function buildCorpusStats(
  articles: ArticleItem[],
  totalHits: number,
): CorpusStats {
  const yearDistribution: Record<string, number> = {};
  const yearQuartileStacked: Record<string, Record<string, number>> = {};
  const quartileCounts: Record<string, number> = {};
  const ifValues: number[] = [];
  let matched = 0;

  for (const a of articles) {
    const q = quartileGroupKey(a.quartile);
    quartileCounts[q] = (quartileCounts[q] ?? 0) + 1;
    if (a.year != null) {
      const yk = String(a.year);
      yearDistribution[yk] = (yearDistribution[yk] ?? 0) + 1;
      if (!yearQuartileStacked[yk]) {
        yearQuartileStacked[yk] = {};
      }
      const inner = yearQuartileStacked[yk];
      inner[q] = (inner[q] ?? 0) + 1;
    }
    if (a.impact_factor != null) {
      ifValues.push(a.impact_factor);
      matched += 1;
    }
  }

  const n = articles.length;
  const rate = n ? matched / n : 0;
  const sorted = [...ifValues].sort((a, b) => a - b);
  let mean: number | null = null;
  let median: number | null = null;
  let minV: number | null = null;
  let maxV: number | null = null;
  if (sorted.length) {
    mean = sorted.reduce((s, x) => s + x, 0) / sorted.length;
    const mid = Math.floor(sorted.length / 2);
    median =
      sorted.length % 2 === 1
        ? sorted[mid]
        : (sorted[mid - 1] + sorted[mid]) / 2;
    minV = sorted[0];
    maxV = sorted[sorted.length - 1];
  }

  const ifSummary: IfSummary = {
    mean,
    median,
    min: minV,
    max: maxV,
    count_matched: matched,
  };

  function yearSortKey(k: string): [number, string] {
    const n = parseInt(k, 10);
    return Number.isFinite(n) ? [n, k] : [0, k];
  }

  const yearKeys = Object.keys(yearDistribution).sort((a, b) => {
    const [na, sa] = yearSortKey(a);
    const [nb, sb] = yearSortKey(b);
    return na !== nb ? na - nb : sa.localeCompare(sb);
  });

  const sortedYearDist: Record<string, number> = {};
  const sortedYq: Record<string, Record<string, number>> = {};
  for (const k of yearKeys) {
    sortedYearDist[k] = yearDistribution[k] ?? 0;
    if (yearQuartileStacked[k]) {
      sortedYq[k] = { ...yearQuartileStacked[k] };
    }
  }

  return {
    total_hits: totalHits,
    analyzed_count: n,
    journal_match_rate: Math.round(rate * 10000) / 10000,
    year_distribution: sortedYearDist,
    quartile_counts: quartileCounts,
    year_quartile_stacked: sortedYq,
    if_summary: ifSummary,
  };
}

/** 与 `top100_if_recent_years` 排序一致。 */
export function top100IfRecentYears(
  articles: ArticleItem[],
  years = 5,
): ArticleItem[] {
  const recent = articles.filter((a) => inLastNYears(a.year, years));

  function sortKey(a: ArticleItem): [number, number, number, string] {
    const hasIf = a.impact_factor != null ? 1 : 0;
    const ifVal = a.impact_factor ?? -1;
    const y = a.year ?? 0;
    return [hasIf, ifVal, y, a.title];
  }

  const ranked = [...recent].sort((a, b) => {
    const ka = sortKey(a);
    const kb = sortKey(b);
    for (let i = 0; i < 4; i++) {
      const cmp = ka[i]! < kb[i]! ? 1 : ka[i]! > kb[i]! ? -1 : 0;
      if (cmp !== 0) return cmp;
    }
    return 0;
  });
  return ranked.slice(0, 100);
}
