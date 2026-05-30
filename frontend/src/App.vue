<!-- [2026-05-19] Top100 不足 100 条时显示语料说明。 -->
<!-- [2026-05-19] MedSci 补全提示移入结果区，与图表并列展示。 -->
<!-- [2026-05-19] 词云再次点击取消 Top100 高亮；新检索清空 highlightWord。 -->
<!-- [2026-05-19] 仅 onSearch 清选中/筛选；MedSci 补全不打断高亮。 -->
<script setup lang="ts">
import { computed, ref } from 'vue';

import SearchBar from '@/components/SearchBar.vue';
import StatsCharts from '@/components/StatsCharts.vue';
import Top100Table from '@/components/Top100Table.vue';
import ReviewPanel from '@/components/ReviewPanel.vue';
import WordCloudView from '@/components/WordCloudView.vue';
import { useAnalyze } from '@/composables/useAnalyze';
import { useDashboardFilters } from '@/composables/useDashboardFilters';

const ANALYZE_MAX_RESULTS = 500;

const tab = ref<'dashboard' | 'review'>('dashboard');
const {
  loading,
  enrichingMetrics,
  error,
  result,
  reviewLoading,
  reviewError,
  runAnalyze,
} = useAnalyze();

const {
  yearRange,
  quartile,
  hasActiveFilters,
  filterLabel,
  filterArticles,
  setQuartile,
  setYearRange,
  clearFilters,
} = useDashboardFilters();

const wordHint = ref<string | null>(null);
const highlightWord = ref<string | null>(null);

const filteredArticles = computed(() => {
  if (!result.value?.articles) {
    return [];
  }
  return filterArticles(result.value.articles);
});

const filteredTop100 = computed(() => {
  if (!result.value?.top100_if_5y) {
    return [];
  }
  return filterArticles(result.value.top100_if_5y);
});

function onSearch(q: string) {
  clearFilters();
  wordHint.value = null;
  highlightWord.value = null;
  runAnalyze(q, ANALYZE_MAX_RESULTS);
}

function onQuartileSelect(q: string | null) {
  setQuartile(q);
}

function onYearRange(range: [number, number] | null) {
  setYearRange(range);
}

/** 函数功能：词云/词条表点击高亮 Top100，再次点击取消。
 *  输入说明：word 为选中词，null 表示取消。
 *  输出说明：无。 */
function onWordClick(word: string | null) {
  highlightWord.value = word;
  if (!word) {
    wordHint.value = null;
    return;
  }
  const lower = word.toLowerCase();
  const hits = filteredTop100.value.filter(
    (r) =>
      r.title.toLowerCase().includes(lower) ||
      (r.abstract?.toLowerCase().includes(lower) ?? false),
  );
  if (!hits.length) {
    wordHint.value = `词「${word}」在近 5 年 Top100 当前视图中无匹配标题/摘要。`;
  } else {
    wordHint.value = `词「${word}」匹配 ${hits.length} 条 Top100 记录（已高亮，再次点击可取消）。`;
  }
}
</script>

<template>
  <div class="app">
    <header class="app-header">
      <div class="app-header-inner">
        <div class="app-header-text">
          <span class="app-header-brand">PubMed 文献分析</span>
          <span class="app-header-sub">PubMed 检索 · 期刊指标 · 语料可视化</span>
        </div>
      </div>
    </header>

    <main class="app-main">
      <SearchBar :loading="loading" @search="onSearch" />

      <div v-if="error" class="alert" role="alert">
        {{ error }}
      </div>

      <div v-if="loading" class="loading-panel panel" aria-busy="true" aria-live="polite">
        <div class="skeleton">
          <div class="sk-line" />
          <div class="sk-line short" />
          <div class="sk-line mid" />
        </div>
        <p class="loading-title">加载中</p>
        <p class="loading-desc">正在检索并分析文献，请稍候…</p>
      </div>

      <div
        v-if="!loading && result && !result.stats.analyzed_count"
        class="empty panel"
      >
        未检索到文献，请调整关键词后重试。
      </div>

      <template v-if="!loading && result">
        <div
          v-if="enrichingMetrics"
          class="enrich-hint panel"
          aria-live="polite"
        >
          <p class="loading-desc">
            正在从 MedSci 补全未知期刊指标，图表将随补全结果更新…
          </p>
        </div>

        <nav class="tabs panel" aria-label="分析视图">
          <button
            type="button"
            class="tab"
            :class="{ active: tab === 'dashboard' }"
            @click="tab = 'dashboard'"
          >
            分析结果
          </button>
          <button
            type="button"
            class="tab"
            :class="{ active: tab === 'review' }"
            @click="tab = 'review'"
          >
            综述
          </button>
        </nav>

        <div
          v-if="hasActiveFilters && tab === 'dashboard'"
          class="filter-banner"
          role="status"
        >
          <span>已筛选：{{ filterLabel }}</span>
          <button type="button" class="filter-banner-clear" @click="clearFilters">
            清除筛选
          </button>
        </div>

        <section v-show="tab === 'dashboard'" class="dashboard">
          <StatsCharts
            :stats="result.stats"
            :articles="filteredArticles"
            :analyzed-total="result.stats.analyzed_count"
            :has-active-filters="hasActiveFilters"
            :active-quartile="quartile"
            :year-range="yearRange"
            @quartile-select="onQuartileSelect"
            @year-range="onYearRange"
          />
          <div class="block">
            <h2 class="section-heading">词云</h2>
            <p class="block-hint muted">
              词云基于全量语料；点击词条可高亮 Top100 表格，再次点击可取消
            </p>
            <WordCloudView
              :items="result.wordcloud"
              :selected-word="highlightWord"
              @word-click="onWordClick"
            />
            <p v-if="wordHint" class="toast-hint">{{ wordHint }}</p>
          </div>
          <div class="block">
            <h2 class="section-heading">
              近 5 年高影响因子文献（Top100）
              <span
                v-if="result.top100_if_5y.length < 100"
                class="heading-count"
              >
                （共 {{ result.top100_if_5y.length }} 条）
              </span>
            </h2>
            <p
              v-if="result.top100_if_5y.length < 100 && !hasActiveFilters"
              class="block-hint muted"
            >
              当前检索已分析 {{ result.stats.analyzed_count }} 篇，其中近 5 年文献
              {{ result.top100_if_5y.length }} 篇；Top100 展示全部可得结果（PubMed
              单次最多拉取 500 条）。
            </p>
            <p v-else-if="hasActiveFilters" class="block-hint muted">
              筛选后 {{ filteredTop100.length }} / {{ result.top100_if_5y.length }} 条
            </p>
            <Top100Table
              :rows="filteredTop100"
              :highlight-word="highlightWord"
            />
          </div>
        </section>

        <section v-show="tab === 'review'" class="section-review">
          <ReviewPanel
            :review="result.review"
            :review-loading="reviewLoading"
            :review-error="reviewError"
          />
        </section>
      </template>

      <div v-if="!loading && !result" class="placeholder panel">
        输入检索式并点击「分析」，结果将显示在此处。
      </div>
    </main>
  </div>
</template>

<style scoped lang="scss">
.app {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
}

.app-header {
  background: var(--header-bg);
  border-bottom: 1px solid rgba(0, 0, 0, 0.12);
  box-shadow: var(--shadow-sm);
}

.app-header-inner {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0.9rem 1rem;
}

.app-header-text {
  display: flex;
  flex-direction: column;
  gap: 0.2rem;
}

.app-header-brand {
  font-size: var(--text-lg);
  font-weight: 600;
  color: var(--header-text);
  letter-spacing: 0.02em;
}

.app-header-sub {
  font-size: var(--text-sm);
  color: rgba(255, 255, 255, 0.85);
}

.app-main {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: var(--space-md);
  max-width: 1200px;
  width: 100%;
  margin: 0 auto;
  padding: var(--space-md) var(--space-md) 2.5rem;
}

.alert {
  padding: 0.65rem 0.85rem;
  border-radius: var(--radius-sm);
  border: 1px solid var(--danger-border);
  background: var(--danger-bg);
  color: var(--danger-text);
  font-size: 0.9rem;
}

.loading-panel {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: var(--space-sm);
  min-height: 220px;
  padding: 2rem 1.5rem;
  width: 100%;
}

.skeleton {
  width: 100%;
  max-width: 320px;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.sk-line {
  height: 0.65rem;
  border-radius: 4px;
  background: linear-gradient(
    90deg,
    rgba(21, 101, 192, 0.08) 0%,
    rgba(21, 101, 192, 0.18) 50%,
    rgba(21, 101, 192, 0.08) 100%
  );
  background-size: 200% 100%;
  animation: sk-shimmer 1.2s ease-in-out infinite;
}

.sk-line.short {
  width: 72%;
}

.sk-line.mid {
  width: 88%;
}

@keyframes sk-shimmer {
  0% {
    background-position: 100% 0;
  }
  100% {
    background-position: -100% 0;
  }
}

.loading-title {
  margin: 0;
  font-size: var(--text-lg);
  font-weight: 600;
}

.loading-desc {
  margin: 0;
  font-size: var(--text-base);
  color: var(--muted);
}

.enrich-hint {
  margin-bottom: 1rem;
  padding: 0.75rem 1rem;
  border-left: 3px solid var(--accent, #1976d2);
}

.empty,
.placeholder {
  padding: 1.5rem 1rem;
  text-align: center;
  color: var(--muted);
  font-size: var(--text-base);
}

.tabs {
  display: inline-flex;
  flex-wrap: wrap;
  gap: 0.35rem;
  padding: 0.35rem;
  align-self: flex-start;
}

.tab {
  padding: 0.45rem 1.1rem;
  border: none;
  border-radius: var(--radius-sm);
  background: transparent;
  color: var(--muted);
  cursor: pointer;
  font-size: 0.92rem;
  font-weight: 500;
  transition:
    background var(--transition-fast),
    color var(--transition-fast);

  &:hover {
    color: var(--accent);
    background: var(--accent-soft);
  }

  &.active {
    color: #fff;
    background: var(--accent);
    font-weight: 600;
    box-shadow: var(--shadow-sm);
  }
}

.dashboard {
  display: flex;
  flex-direction: column;
  gap: var(--space-lg);
}

.block {
  display: flex;
  flex-direction: column;
  gap: var(--space-sm);
}

.block-hint {
  margin: 0;
  font-size: var(--text-sm);
}

.muted {
  color: var(--muted);
}

.section-review {
  padding-top: 0.25rem;
}
</style>
