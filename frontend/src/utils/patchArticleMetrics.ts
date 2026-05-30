/** [2026-05-19] 将 MedSci 补全条目合并到文献列表。 */
import type { ArticleItem, MetricsEnrichmentEntry } from '@/api/analyze';

/**
 * 功能：按 ISSN 优先、刊名次之，将 new_entries 写入 articles。
 * 输入说明：articles 列表、补全条目列表。
 * 输出说明：新 articles 数组（浅拷贝条目）。
 */
export function patchArticlesWithMetrics(
  articles: ArticleItem[],
  entries: MetricsEnrichmentEntry[],
): ArticleItem[] {
  if (!entries.length) {
    return articles;
  }
  const byIssn = new Map<string, MetricsEnrichmentEntry>();
  const byTitle = new Map<string, MetricsEnrichmentEntry>();
  for (const e of entries) {
    const issn = normalizeIssn(e.issn);
    if (issn) {
      byIssn.set(issn, e);
    }
    const t = normalizeTitle(e.journal_name);
    if (t) {
      byTitle.set(t, e);
    }
  }
  return articles.map((a) => {
    const hit =
      (a.issn && byIssn.get(normalizeIssn(a.issn) ?? '')) ||
      (a.journal && byTitle.get(normalizeTitle(a.journal) ?? ''));
    if (!hit) {
      return a;
    }
    return {
      ...a,
      impact_factor:
        hit.impact_factor !== undefined && hit.impact_factor !== null
          ? hit.impact_factor
          : a.impact_factor,
      quartile: hit.quartile ?? a.quartile,
    };
  });
}

function normalizeIssn(raw: string | null | undefined): string | null {
  if (!raw) {
    return null;
  }
  const s = raw.replace(/[^0-9Xx]/g, '').toLowerCase();
  return s || null;
}

function normalizeTitle(title: string | null | undefined): string | null {
  if (!title) {
    return null;
  }
  return title
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, ' ')
    .trim()
    .replace(/\s+/g, ' ');
}
