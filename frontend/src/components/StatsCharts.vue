<script setup lang="ts">
import { computed } from 'vue';

import type { CorpusStats } from '@/api/analyze';

const C_TEXT = '#37474f';
const C_MUTED = '#78909c';
const C_AXIS = '#b0bec5';
const C_SPLIT = '#eceff1';

const props = defineProps<{
  stats: CorpusStats | null;
}>();

const yearOption = computed(() => {
  const s = props.stats;
  if (!s || !Object.keys(s.year_distribution).length) {
    return {
      backgroundColor: 'transparent',
      textStyle: { color: C_TEXT },
      title: {
        text: '暂无年份数据',
        left: 'center',
        top: 'middle',
        textStyle: { color: C_MUTED, fontSize: 14 },
      },
    };
  }
  const years = Object.keys(s.year_distribution).sort();
  const vals = years.map((y) => s.year_distribution[y] ?? 0);
  return {
    backgroundColor: 'transparent',
    textStyle: { color: C_TEXT },
    tooltip: {
      trigger: 'axis',
      backgroundColor: '#fff',
      borderColor: C_AXIS,
      textStyle: { color: C_TEXT },
    },
    grid: { left: 48, right: 16, top: 32, bottom: 40 },
    xAxis: {
      type: 'category',
      data: years,
      axisLine: { lineStyle: { color: C_AXIS } },
      axisLabel: {
        rotate: years.length > 12 ? 35 : 0,
        color: C_MUTED,
      },
    },
    yAxis: {
      type: 'value',
      name: '篇数',
      nameTextStyle: { color: C_MUTED },
      axisLine: { show: true, lineStyle: { color: C_AXIS } },
      axisLabel: { color: C_MUTED },
      splitLine: { lineStyle: { color: C_SPLIT } },
    },
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
              { offset: 0, color: '#1976d2' },
              { offset: 1, color: '#0d47a1' },
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
      textStyle: { color: C_TEXT },
      title: {
        text: '暂无分区数据',
        left: 'center',
        top: 'middle',
        textStyle: { color: C_MUTED, fontSize: 14 },
      },
    };
  }
  const entries = Object.entries(s.quartile_counts);
  const data = entries.map(([name, value]) => ({ name, value }));
  const pieColors = ['#1565c0', '#1976d2', '#42a5f5', '#90caf9', '#78909c'];
  return {
    backgroundColor: 'transparent',
    textStyle: { color: C_TEXT },
    tooltip: {
      trigger: 'item',
      backgroundColor: '#fff',
      borderColor: C_AXIS,
      textStyle: { color: C_TEXT },
    },
    legend: {
      bottom: 0,
      textStyle: { color: C_MUTED },
    },
    series: [
      {
        type: 'pie',
        radius: ['36%', '62%'],
        data,
        label: { color: C_TEXT },
        color: pieColors,
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
    color: var(--text);
  }
}

.if-box {
  font-size: 0.88rem;
  line-height: 1.5;
  padding: 0.65rem 0.85rem;
  background: var(--surface-elevated);
  border: 1px solid var(--border);
  border-radius: var(--radius);
}

.if-title {
  display: block;
  font-weight: 600;
  margin-bottom: 0.35rem;
  color: var(--text);
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
