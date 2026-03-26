<script setup lang="ts">
import { ref } from 'vue';

import SearchBar from '@/components/SearchBar.vue';
import StatsCharts from '@/components/StatsCharts.vue';
import Top100Table from '@/components/Top100Table.vue';
import ReviewPanel from '@/components/ReviewPanel.vue';
import WordCloudView from '@/components/WordCloudView.vue';
import { useAnalyze } from '@/composables/useAnalyze';

const ANALYZE_MAX_RESULTS = 100;

const tab = ref<'dashboard' | 'review'>('dashboard');
const { loading, error, result, reviewLoading, reviewError, runAnalyze } =
  useAnalyze();

function onSearch(q: string) {
  runAnalyze(q, ANALYZE_MAX_RESULTS);
}
</script>

<template>
  <div class="app">
    <header class="app-header">
      <div class="app-header-inner">
        <span class="app-header-brand">PubMed 文献分析</span>
      </div>
    </header>

    <main class="app-main">
      <SearchBar :loading="loading" @search="onSearch" />

      <div v-if="error" class="alert" role="alert">
        {{ error }}
      </div>

      <div v-if="loading" class="loading-panel" aria-busy="true" aria-live="polite">
        <div class="spinner" />
        <p class="loading-title">加载中</p>
        <p class="loading-desc">正在检索并分析文献，请稍候…</p>
      </div>

      <div v-else-if="result && !result.stats.analyzed_count" class="empty">
        未检索到文献，请调整关键词后重试。
      </div>

      <template v-else-if="result">
        <nav class="tabs" aria-label="分析视图">
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

        <section v-show="tab === 'dashboard'" class="dashboard">
          <StatsCharts :stats="result.stats" />
          <div class="block">
            <h2 class="section-title">词云</h2>
            <WordCloudView :items="result.wordcloud" />
          </div>
          <div class="block">
            <h2 class="section-title">近 5 年高影响因子文献（Top100）</h2>
            <Top100Table :rows="result.top100_if_5y" />
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

      <div v-else class="placeholder">
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
  border-bottom: 1px solid var(--border);
  box-shadow: 0 1px 0 rgba(0, 0, 0, 0.04);
}

.app-header-inner {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0.75rem 1rem;
}

.app-header-brand {
  font-size: 1.05rem;
  font-weight: 600;
  color: var(--header-text);
  letter-spacing: 0.02em;
}

.app-main {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 1rem;
  max-width: 1200px;
  width: 100%;
  margin: 0 auto;
  padding: 1rem 1rem 2.5rem;
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
  gap: 0.75rem;
  min-height: 220px;
  padding: 2rem 1.5rem;
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  color: var(--text);
}

.spinner {
  width: 40px;
  height: 40px;
  border: 3px solid var(--border);
  border-top-color: var(--accent);
  border-radius: 50%;
  animation: spin 0.75s linear infinite;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

.loading-title {
  margin: 0;
  font-size: 1.05rem;
  font-weight: 600;
}

.loading-desc {
  margin: 0;
  font-size: 0.9rem;
  color: var(--muted);
}

.empty,
.placeholder {
  padding: 1.5rem 1rem;
  text-align: center;
  color: var(--muted);
  border: 1px dashed var(--border);
  border-radius: var(--radius);
  font-size: 0.95rem;
  background: var(--surface);
}

.tabs {
  display: flex;
  flex-wrap: wrap;
  gap: 0;
  border-bottom: 2px solid var(--border);
}

.tab {
  position: relative;
  padding: 0.55rem 1.25rem;
  margin-bottom: -2px;
  border: none;
  border-bottom: 2px solid transparent;
  background: transparent;
  color: var(--muted);
  cursor: pointer;
  font-size: 0.92rem;
  font-weight: 500;

  &:hover {
    color: var(--accent);
    background: var(--accent-soft);
  }

  &.active {
    color: var(--accent);
    border-bottom-color: var(--accent);
    font-weight: 600;
  }
}

.dashboard {
  display: flex;
  flex-direction: column;
  gap: 1.75rem;
}

.block {
  display: flex;
  flex-direction: column;
  gap: 0.65rem;
}

.section-title {
  margin: 0;
  font-size: 1.05rem;
  font-weight: 600;
  color: var(--text);
  padding-bottom: 0.35rem;
  border-bottom: 1px solid var(--border);
}

.section-review {
  padding-top: 0.25rem;
}
</style>
