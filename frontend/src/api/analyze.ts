/** [2026-05-19] 关页 keepalive 取消 MedSci 补全任务。 */
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

export interface MetricsEnrichmentInfo {
  job_id: string | null;
  pending_count: number;
  needs_enrichment: boolean;
}

export interface MetricsEnrichmentEntry {
  journal_name: string | null;
  issn: string | null;
  impact_factor: number | null;
  quartile: string | null;
  cas_bigclass?: string | null;
}

export interface MetricsEnrichmentSyncResponse {
  job_id: string;
  status: 'running' | 'completed' | 'cancelled';
  sync_enriched_count: number;
  pending_count: number;
  failed_count: number;
  seq: number;
  new_entries: MetricsEnrichmentEntry[];
  background_started: boolean;
}

export interface MetricsEnrichmentPollResponse {
  job_id: string;
  status: 'running' | 'completed' | 'cancelled';
  pending_count: number;
  failed_count: number;
  seq: number;
  new_entries: MetricsEnrichmentEntry[];
}

/** 后端 /api/analyze 原始响应 */
export interface AnalyzeApiResponse {
  articles: ArticleItem[];
  total_hits: number;
  /** 首次分析为 null；由 postReview 填充 */
  review: ReviewPayload | null;
  enrichment?: MetricsEnrichmentInfo | null;
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

async function parseApiError(res: Response): Promise<string> {
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
  return detail || `HTTP ${res.status}`;
}

export async function postMetricsEnrichmentSync(
  jobId: string,
  limit?: number,
): Promise<MetricsEnrichmentSyncResponse> {
  const q = limit != null ? `?limit=${limit}` : '';
  const url = apiUrl(`/api/metrics-enrichment/${encodeURIComponent(jobId)}/sync${q}`);
  const res = await fetch(url, { method: 'POST' });
  if (!res.ok) {
    throw new Error(await parseApiError(res));
  }
  return res.json() as Promise<MetricsEnrichmentSyncResponse>;
}

export async function getMetricsEnrichment(
  jobId: string,
  sinceSeq = 0,
): Promise<MetricsEnrichmentPollResponse> {
  const url = apiUrl(
    `/api/metrics-enrichment/${encodeURIComponent(jobId)}?since_seq=${sinceSeq}`,
  );
  const res = await fetch(url);
  if (!res.ok) {
    throw new Error(await parseApiError(res));
  }
  return res.json() as Promise<MetricsEnrichmentPollResponse>;
}

/**
 * 功能：取消 MedSci 指标补全任务。
 * 输入说明：job_id。
 * 输出说明：无；失败抛错。
 */
export async function postMetricsEnrichmentCancel(jobId: string): Promise<void> {
  const url = apiUrl(
    `/api/metrics-enrichment/${encodeURIComponent(jobId)}/cancel`,
  );
  const res = await fetch(url, { method: 'POST' });
  if (!res.ok) {
    throw new Error(await parseApiError(res));
  }
}

/**
 * 功能：关页/刷新时用 keepalive 发送取消（不等待响应）。
 * 输入说明：job_id。
 * 输出说明：无。
 */
export function postMetricsEnrichmentCancelKeepalive(jobId: string): void {
  const url = apiUrl(
    `/api/metrics-enrichment/${encodeURIComponent(jobId)}/cancel`,
  );
  void fetch(url, { method: 'POST', keepalive: true }).catch(() => {});
}
