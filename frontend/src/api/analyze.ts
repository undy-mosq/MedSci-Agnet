/** POST /api/analyze 类型与封装。 */

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

export interface AnalyzeResponse {
  articles: ArticleItem[];
  stats: CorpusStats;
  top100_if_5y: ArticleItem[];
  wordcloud: WordCloudItem[];
  review: ReviewPayload;
}

function apiBase(): string {
  const b = import.meta.env.VITE_API_BASE ?? '';
  return b.replace(/\/$/, '');
}

export async function postAnalyze(
  body: AnalyzeRequestBody,
): Promise<AnalyzeResponse> {
  const url = `${apiBase()}/api/analyze`;
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
  return res.json() as Promise<AnalyzeResponse>;
}
