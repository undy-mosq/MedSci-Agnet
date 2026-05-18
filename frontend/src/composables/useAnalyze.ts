/** [2026-05-18] 编排 analyze + 前端统计/词云 + review。 */
import { ref } from 'vue';

import {
  postAnalyze,
  type AnalyzeApiResponse,
  type AnalyzeResult,
} from '@/api/analyze';
import { postReview } from '@/api/review';
import { buildCorpusStats, top100IfRecentYears } from '@/utils/corpusStats';
import { buildWordFrequencies } from '@/utils/wordFreq';

/**
 * 功能：将 analyze API 响应扩展为含 stats、词云、Top100 的完整结果。
 * 输入说明：后端返回的 articles 与 total_hits。
 * 输出说明：供 UI 使用的 AnalyzeResult。
 */
function enrichAnalyzeResult(raw: AnalyzeApiResponse): AnalyzeResult {
  const { articles, total_hits } = raw;
  const stats = buildCorpusStats(articles, total_hits);
  const top100_if_5y = top100IfRecentYears(articles, 5);
  const texts = articles.map(
    (a) => `${a.title} ${a.abstract ?? ''}`.trim(),
  );
  const wordcloud = buildWordFrequencies(texts, 100);
  return {
    ...raw,
    stats,
    top100_if_5y,
    wordcloud,
  };
}

export function useAnalyze() {
  const loading = ref(false);
  const error = ref<string | null>(null);
  const result = ref<AnalyzeResult | null>(null);
  const reviewLoading = ref(false);
  const reviewError = ref<string | null>(null);

  async function runAnalyze(query: string, maxResults: number) {
    loading.value = true;
    error.value = null;
    reviewError.value = null;
    result.value = null;
    reviewLoading.value = false;
    let first: AnalyzeResult | null = null;
    try {
      const raw = await postAnalyze({
        query: query.trim(),
        max_results: maxResults,
      });
      first = enrichAnalyzeResult(raw);
      result.value = first;
    } catch (e) {
      error.value = e instanceof Error ? e.message : String(e);
    } finally {
      loading.value = false;
    }

    if (first && first.stats.analyzed_count > 0) {
      reviewLoading.value = true;
      try {
        const review = await postReview({
          query: query.trim(),
          stats: first.stats,
          articles: first.articles,
        });
        if (result.value) {
          result.value = { ...result.value, review };
        }
      } catch (e) {
        reviewError.value = e instanceof Error ? e.message : String(e);
      } finally {
        reviewLoading.value = false;
      }
    }
  }

  return {
    loading,
    error,
    result,
    reviewLoading,
    reviewError,
    runAnalyze,
  };
}
