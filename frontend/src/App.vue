<script setup lang="ts">
import { ref } from 'vue';

import SearchBar from '@/components/SearchBar.vue';
import StatsCharts from '@/components/StatsCharts.vue';
import Top100Table from '@/components/Top100Table.vue';
import ReviewPanel from '@/components/ReviewPanel.vue';
import WordCloudView from '@/components/WordCloudView.vue';
import { useAnalyze } from '@/composables/useAnalyze';

const tab = ref<'stats' | 'cloud' | 'top' | 'review'>('stats');
const { loading, error, result, runAnalyze } = useAnalyze();

function onSearch(q: string, max: number) {
  runAnalyze(q, max);
}
</script>

<template>
  <div class="app">
    <SearchBar :loading="loading" @search="onSearch" />

    <div v-if="error" class="alert" role="alert">
      {{ error }}
    </div>

    <div v-if="loading" class="loading">正在从 PubMed 拉取并分析…</div>

    <div v-else-if="result && !result.stats.analyzed_count" class="empty">
      未检索到文献，请调整关键词或条数。
    </div>

    <template v-else-if="result">
      <nav class="tabs" aria-label="分析视图">
        <button
          type="button"
          class="tab"
          :class="{ active: tab === 'stats' }"
          @click="tab = 'stats'"
        >
          统计图表
        </button>
        <button
          type="button"
          class="tab"
          :class="{ active: tab === 'cloud' }"
          @click="tab = 'cloud'"
        >
          词云
        </button>
        <button
          type="button"
          class="tab"
          :class="{ active: tab === 'top' }"
          @click="tab = 'top'"
        >
          近5年 Top100
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

      <section v-show="tab === 'stats'" class="section">
        <StatsCharts :stats="result.stats" />
      </section>
      <section v-show="tab === 'cloud'" class="section">
        <WordCloudView :items="result.wordcloud" />
      </section>
      <section v-show="tab === 'top'" class="section">
        <Top100Table :rows="result.top100_if_5y" />
      </section>
      <section v-show="tab === 'review'" class="section">
        <ReviewPanel :review="result.review" />
      </section>
    </template>

    <div v-else class="placeholder">
      输入检索式并点击「分析」，结果将显示在此处。
    </div>
  </div>
</template>

<style scoped lang="scss">
.app {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.alert {
  padding: 0.65rem 0.85rem;
  border-radius: var(--radius);
  border: 1px solid rgba(248, 113, 113, 0.45);
  background: rgba(127, 29, 29, 0.25);
  color: #fecaca;
  font-size: 0.9rem;
}

.loading {
  padding: 1rem;
  text-align: center;
  color: var(--muted);
  font-size: 0.95rem;
}

.empty,
.placeholder {
  padding: 1.5rem 1rem;
  text-align: center;
  color: var(--muted);
  border: 1px dashed var(--border);
  border-radius: var(--radius);
  font-size: 0.95rem;
}

.tabs {
  display: flex;
  flex-wrap: wrap;
  gap: 0.35rem;
  border-bottom: 1px solid var(--border);
  padding-bottom: 0.5rem;
}

.tab {
  padding: 0.4rem 0.85rem;
  border: 1px solid transparent;
  border-radius: 999px;
  background: transparent;
  color: var(--muted);
  cursor: pointer;
  font-size: 0.88rem;

  &:hover {
    color: var(--text);
    background: rgba(61, 139, 253, 0.12);
  }

  &.active {
    color: #fff;
    background: rgba(61, 139, 253, 0.35);
    border-color: rgba(61, 139, 253, 0.5);
  }
}

.section {
  padding-top: 0.25rem;
}
</style>
