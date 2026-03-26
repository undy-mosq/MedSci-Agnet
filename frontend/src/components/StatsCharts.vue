<script setup lang="ts">
import { computed } from 'vue';

import type { CorpusStats } from '@/api/analyze';

const props = defineProps<{
  stats: CorpusStats | null;
}>();

const yearOption = computed(() => {
  const s = props.stats;
  if (!s || !Object.keys(s.year_distribution).length) {
    return {
      backgroundColor: 'transparent',
      textStyle: { color: '#e8edf5' },
      title: {
        text: '暂无年份数据',
        left: 'center',
        top: 'middle',
        textStyle: { color: '#8b9bb4', fontSize: 14 },
      },
    };
  }
  const years = Object.keys(s.year_distribution).sort();
  const vals = years.map((y) => s.year_distribution[y] ?? 0);
  return {
    backgroundColor: 'transparent',
    textStyle: { color: '#e8edf5' },
    tooltip: { trigger: 'axis' },
    grid: { left: 48, right: 16, top: 32, bottom: 40 },
    xAxis: {
      type: 'category',
      data: years,
      axisLabel: { rotate: years.length > 12 ? 35 : 0 },
    },
    yAxis: { type: 'value', name: '篇数' },
    series: [
      {
        type: 'bar',
        data: vals,
        itemStyle: {
          color: {
            type: 'linear',
            x: 0,
            y: 0,
            x2: 0,
            y2: 1,
            colorStops: [
              { offset: 0, color: '#3d8bfd' },
              { offset: 1, color: '#1e3a5f' },
            ],
          },
        },
      },
    ],
  };
});

const quartileOption = computed(() => {
  const s = props.stats;
  if (!s || !Object.keys(s.quartile_counts).length) {
    return {
      backgroundColor: 'transparent',
      textStyle: { color: '#e8edf5' },
      title: {
        text: '暂无分区数据',
        left: 'center',
        top: 'middle',
        textStyle: { color: '#8b9bb4', fontSize: 14 },
      },
    };
  }
  const entries = Object.entries(s.quartile_counts);
  const data = entries.map(([name, value]) => ({ name, value }));
  return {
    backgroundColor: 'transparent',
    textStyle: { color: '#e8edf5' },
    tooltip: { trigger: 'item' },
    legend: { bottom: 0, textStyle: { color: '#8b9bb4' } },
    series: [
      {
        type: 'pie',
        radius: ['36%', '62%'],
        data,
        label: { color: '#e8edf5' },
      },
    ],
  };
});

const ifText = computed(() => {
  const s = props.stats?.if_summary;
  if (!s) {
    return null;
  }
  return {
    mean: s.mean,
    median: s.median,
    min: s.min,
    max: s.max,
    n: s.count_matched,
  };
});
</script>

<template>
  <div v-if="stats" class="stats">
    <section class="cards">
      <div class="card">
        <span class="label">检索命中</span>
        <strong>{{ stats.total_hits }}</strong>
      </div>
      <div class="card">
        <span class="label">本次分析</span>
        <strong>{{ stats.analyzed_count }}</strong>
      </div>
      <div class="card">
        <span class="label">期刊匹配率</span>
        <strong>{{ (stats.journal_match_rate * 100).toFixed(1) }}%</strong>
      </div>
    </section>
    <div v-if="ifText" class="if-box">
      <span class="if-title">影响因子（已匹配 {{ ifText.n }} 篇）</span>
      <span v-if="ifText.n === 0" class="muted">无匹配期刊，无法计算 IF 统计。</span>
      <template v-else>
        均值 {{ ifText.mean?.toFixed(2) ?? '—' }} · 中位数
        {{ ifText.median?.toFixed(2) ?? '—' }} · 最小
        {{ ifText.min?.toFixed(2) ?? '—' }} · 最大 {{ ifText.max?.toFixed(2) ?? '—' }}
      </template>
    </div>
    <div class="charts">
      <div class="chart-wrap">
        <h3 class="chart-title">年份分布</h3>
        <v-chart class="chart" :option="yearOption" autoresize />
      </div>
      <div class="chart-wrap">
        <h3 class="chart-title">分区分布</h3>
        <v-chart class="chart" :option="quartileOption" autoresize />
      </div>
    </div>
  </div>
  <p v-else class="muted">暂无统计数据。</p>
</template>

<style scoped lang="scss">
.stats {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
  gap: 0.65rem;
}

.card {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  padding: 0.75rem 1rem;
  display: flex;
  flex-direction: column;
  gap: 0.25rem;

  .label {
    font-size: 0.8rem;
    color: var(--muted);
  }

  strong {
    font-size: 1.35rem;
    font-variant-numeric: tabular-nums;
  }
}

.if-box {
  font-size: 0.88rem;
  line-height: 1.5;
  padding: 0.65rem 0.85rem;
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: var(--radius);
}

.if-title {
  display: block;
  font-weight: 600;
  margin-bottom: 0.35rem;
}

.muted {
  color: var(--muted);
}

.charts {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 1rem;
}

.chart-wrap {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  padding: 0.5rem 0.5rem 0.25rem;
}

.chart-title {
  margin: 0 0 0.25rem 0.35rem;
  font-size: 0.9rem;
  font-weight: 600;
  color: var(--muted);
}

.chart {
  height: 280px;
  width: 100%;
}
</style>
