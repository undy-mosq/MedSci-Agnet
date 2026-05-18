/** [2026-05-18] POST /api/review 类型与封装；API 根路径见 client.ts。 */

import type { ArticleItem, CorpusStats, ReviewPayload } from './analyze';
import { apiUrl } from './client';

export interface ReviewRequestBody {
  query: string;
  stats: CorpusStats;
  articles: ArticleItem[];
}

export async function postReview(
  body: ReviewRequestBody,
): Promise<ReviewPayload> {
  const url = apiUrl('/api/review');
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
  return res.json() as Promise<ReviewPayload>;
}
