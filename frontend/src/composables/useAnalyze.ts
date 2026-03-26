import { ref } from 'vue';

import { postAnalyze, type AnalyzeResponse } from '@/api/analyze';

export function useAnalyze() {
  const loading = ref(false);
  const error = ref<string | null>(null);
  const result = ref<AnalyzeResponse | null>(null);

  async function runAnalyze(query: string, maxResults: number) {
    loading.value = true;
    error.value = null;
    result.value = null;
    try {
      result.value = await postAnalyze({
        query: query.trim(),
        max_results: maxResults,
      });
    } catch (e) {
      error.value = e instanceof Error ? e.message : String(e);
    } finally {
      loading.value = false;
    }
  }

  return { loading, error, result, runAnalyze };
}
