/** POST /api/review 类型与封装。 */

import type { ArticleItem, CorpusStats, ReviewPayload } from './analyze';

export interface ReviewRequestBody {
  query: string;
  stats: CorpusStats;
  articles: ArticleItem[];
}

function apiBase(): string {
  const b = import.meta.env.VITE_API_BASE ?? '';
  return b.replace(/\/$/, '');
}

export async function postReview(
  body: ReviewRequestBody,
): Promise<ReviewPayload> {
  const url = `${apiBase()}/api/review`;
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
