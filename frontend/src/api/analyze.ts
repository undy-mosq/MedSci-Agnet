/** [2026-05-18] POST /api/analyze 瘦身为题录+total_hits；统计/词云见 AnalyzeResult。 */
import { apiUrl } from './client';

export interface AnalyzeRequestBody {
  query: string;
  max_results: number;
}

export interface IfSummary {
  mean: number | null;
  median: number | null;
  min: number | null;
  max: number | null;
  count_matched: number;
}

export interface CorpusStats {
  total_hits: number;
  analyzed_count: number;
  journal_match_rate: number;
  year_distribution: Record<string, number>;
  quartile_counts: Record<string, number>;
  /** 年份 -> 分区 -> 篇数，与年份堆积柱一致 */
  year_quartile_stacked: Record<string, Record<string, number>>;
  if_summary: IfSummary;
}

export interface ArticleItem {
  pmid: string;
  title: string;
  abstract: string | null;
  journal: string | null;
  issn: string | null;
  year: number | null;
  authors: string[];
  impact_factor: number | null;
  quartile: string | null;
}

export interface WordCloudItem {
  word: string;
  weight: number;
}

export interface ReviewPayload {
  text: string;
  mode: 'template' | 'llm';
}

/** 后端 /api/analyze 原始响应 */
export interface AnalyzeApiResponse {
  articles: ArticleItem[];
  total_hits: number;
  /** 首次分析为 null；由 postReview 填充 */
  review: ReviewPayload | null;
}

/** 前端合并统计/词云/Top100 后的完整展示结果 */
export interface AnalyzeResult extends AnalyzeApiResponse {
  stats: CorpusStats;
  top100_if_5y: ArticleItem[];
  wordcloud: WordCloudItem[];
}

export async function postAnalyze(
  body: AnalyzeRequestBody,
): Promise<AnalyzeApiResponse> {
  const url = apiUrl('/api/analyze');
  const res = await fetch(url, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  });
  if (!res.ok) {
    let detail = res.statusText;
    try {
      const err: unknown = await res.json();
      if (err && typeof err === 'object' && 'detail' in err) {
        const d = (err as { detail: unknown }).detail;
        if (typeof d === 'string') {
          detail = d;
        } else if (Array.isArray(d)) {
          detail = d.map((x) => JSON.stringify(x)).join('; ');
        } else if (d != null) {
          detail = String(d);
        }
      }
    } catch {
      /* ignore */
    }
    throw new Error(detail || `HTTP ${res.status}`);
  }
  return res.json() as Promise<AnalyzeApiResponse>;
}
