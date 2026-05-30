/** [2026-05-19] 关页 pagehide、新检索取消旧 job；补全 sync + poll。 */

import { onMounted, onUnmounted, ref } from 'vue';



import {

  getMetricsEnrichment,

  postAnalyze,

  postMetricsEnrichmentCancel,

  postMetricsEnrichmentCancelKeepalive,

  postMetricsEnrichmentSync,

  type AnalyzeApiResponse,

  type AnalyzeResult,

  type MetricsEnrichmentEntry,

} from '@/api/analyze';

import { postReview } from '@/api/review';

import { patchArticlesWithMetrics } from '@/utils/patchArticleMetrics';

import { buildCorpusStats, top100IfRecentYears } from '@/utils/corpusStats';

import { buildWordFrequencies } from '@/utils/wordFreq';



const POLL_MS = 2000;

const MAX_POLL_MS = 30 * 60 * 1000;



/**

 * 功能：将 analyze API 响应扩展为含 stats、词云、Top100 的完整结果。

 * 输入说明：后端返回的 articles 与 total_hits 等。

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



function applyMetricPatches(

  base: AnalyzeResult,

  entries: MetricsEnrichmentEntry[],

): AnalyzeResult {

  const articles = patchArticlesWithMetrics(base.articles, entries);

  return enrichAnalyzeResult({

    ...base,

    articles,

  });

}



export function useAnalyze() {

  const loading = ref(false);

  const enrichingMetrics = ref(false);

  const error = ref<string | null>(null);

  const result = ref<AnalyzeResult | null>(null);

  const reviewLoading = ref(false);

  const reviewError = ref<string | null>(null);



  let pollTimer: ReturnType<typeof setInterval> | null = null;

  let activeJobId: string | null = null;

  let pollStartedAt = 0;

  let sinceSeq = 0;



  function clearPoll() {

    if (pollTimer != null) {

      clearInterval(pollTimer);

      pollTimer = null;

    }

    activeJobId = null;

  }



  /**

   * 功能：停止轮询并取消当前补全任务。

   * 输入说明：无。

   * 输出说明：Promise，取消失败被忽略。

   */

  async function cancelActiveEnrichment(): Promise<void> {

    const jobId = activeJobId;

    clearPoll();

    if (jobId) {

      await postMetricsEnrichmentCancel(jobId).catch(() => {});

    }

  }



  function onPageHide(e: PageTransitionEvent) {

    if (e.persisted) {

      return;

    }

    const jobId = activeJobId;

    if (jobId) {

      postMetricsEnrichmentCancelKeepalive(jobId);

    }

  }



  onMounted(() => {

    window.addEventListener('pagehide', onPageHide);

  });



  onUnmounted(() => {

    window.removeEventListener('pagehide', onPageHide);

    void cancelActiveEnrichment();

  });



  async function runEnrichmentPipeline(

    jobId: string,

    base: AnalyzeResult,

  ): Promise<void> {

    enrichingMetrics.value = true;

    sinceSeq = 0;

    let current = base;

    try {

      const sync = await postMetricsEnrichmentSync(jobId);

      sinceSeq = sync.seq;

      if (sync.new_entries.length) {

        current = applyMetricPatches(current, sync.new_entries);

        result.value = current;

      }

      if (sync.status === 'completed' || !sync.background_started) {

        enrichingMetrics.value = false;

        return;

      }

      activeJobId = jobId;

      pollStartedAt = Date.now();

      pollTimer = setInterval(async () => {

        if (!activeJobId || !result.value) {

          clearPoll();

          return;

        }

        if (Date.now() - pollStartedAt > MAX_POLL_MS) {

          await cancelActiveEnrichment();

          enrichingMetrics.value = false;

          return;

        }

        try {

          const poll = await getMetricsEnrichment(activeJobId, sinceSeq);

          sinceSeq = poll.seq;

          if (poll.new_entries.length && result.value) {

            result.value = applyMetricPatches(result.value, poll.new_entries);

          }

          if (poll.status === 'completed' || poll.status === 'cancelled') {

            clearPoll();

            enrichingMetrics.value = false;

          }

        } catch {

          await cancelActiveEnrichment();

          enrichingMetrics.value = false;

        }

      }, POLL_MS);

    } catch {

      enrichingMetrics.value = false;

    }

    if (!pollTimer) {

      enrichingMetrics.value = false;

    }

  }



  async function runAnalyze(query: string, maxResults: number) {

    await cancelActiveEnrichment();

    loading.value = true;

    error.value = null;

    reviewError.value = null;

    result.value = null;

    reviewLoading.value = false;

    enrichingMetrics.value = false;



    let first: AnalyzeResult | null = null;

    try {

      const raw = await postAnalyze({

        query: query.trim(),

        max_results: maxResults,

      });

      first = enrichAnalyzeResult(raw);

      result.value = first;



      const jobId = raw.enrichment?.job_id;

      if (raw.enrichment?.needs_enrichment && jobId) {

        void runEnrichmentPipeline(jobId, first);

      }

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

    enrichingMetrics,

    error,

    result,

    reviewLoading,

    reviewError,

    runAnalyze,

  };

}

