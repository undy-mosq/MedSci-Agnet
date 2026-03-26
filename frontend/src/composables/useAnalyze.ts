import { ref } from 'vue';

import { postAnalyze, type AnalyzeResponse } from '@/api/analyze';
import { postReview } from '@/api/review';

export function useAnalyze() {
  const loading = ref(false);
  const error = ref<string | null>(null);
  const result = ref<AnalyzeResponse | null>(null);
  const reviewLoading = ref(false);
  const reviewError = ref<string | null>(null);

  async function runAnalyze(query: string, maxResults: number) {
    loading.value = true;
    error.value = null;
    reviewError.value = null;
    result.value = null;
    reviewLoading.value = false;
    let first: AnalyzeResponse | null = null;
    try {
      first = await postAnalyze({
        query: query.trim(),
        max_results: maxResults,
      });
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
