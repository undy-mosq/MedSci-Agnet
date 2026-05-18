<!-- [2026-05-18] 年份公共拉条置顶；移除年份图 dataZoom。 -->
<script setup lang="ts">
import { computed } from 'vue';

import type { ArticleItem, CorpusStats } from '@/api/analyze';
import YearRangeBar from '@/components/YearRangeBar.vue';
import {
  abstractCoverage,
  ifHistogram,
  topJournals,
} from '@/utils/articleAggregates';
import { quartileKeysForStack, quartileSectorColor } from '@/utils/chartPalette';
import {
  CHART_COLORS,
  categoryAxis,
  chartGrid,
  dataZoomForJournals,
  echartsBase,
  valueAxis,
} from '@/utils/echartsTheme';

const props = defineProps<{
  stats: CorpusStats | null;
  articles: ArticleItem[];
  analyzedTotal?: number;
  hasActiveFilters?: boolean;
  activeQuartile?: string | null;
  yearRange?: [number, number] | null;
}>();

const emit = defineEmits<{
  'quartile-select': [quartile: string | null];
  'year-range': [range: [number, number] | null];
}>();

const coverage = computed(() => abstractCoverage(props.articles));
const journals = computed(() => topJournals(props.articles, 12));
const ifBins = computed(() => ifHistogram(props.articles, 8));

const matchRateWarning = computed(() => {
  const r = props.stats?.journal_match_rate ?? 0;
  return r > 0 && r < 0.5;
});

const sortedYears = computed(() => {
  const s = props.stats;
  if (!s) {
    return [];
  }
  return Object.keys(s.year_distribution).sort((a, b) => {
    const na = parseInt(a, 10);
    const nb = parseInt(b, 10);
    if (Number.isFinite(na) && Number.isFinite(nb)) return na - nb;
    return a.localeCompare(b);
  });
});

const yearOption = computed(() => {
  const s = props.stats;
  if (!s || !Object.keys(s.year_distribution).length) {
    return echartsBase({
      title: {
        text: '暂无年份数据',
        left: 'center',
        top: 'middle',
        textStyle: { color: CHART_COLORS.muted, fontSize: 14 },
      },
    });
  }
  const years = sortedYears.value;
  const yq = s.year_quartile_stacked ?? {};
  const keySet = new Set<string>();
  for (const y of years) {
    const row = yq[y];
    if (row) {
      Object.keys(row).forEach((k) => keySet.add(k));
    }
  }
  const qKeys = quartileKeysForStack(keySet);
  const bottom = qKeys.length > 5 ? 56 : 44;

  if (qKeys.length === 0) {
    const vals = years.map((y) => s.year_distribution[y] ?? 0);
    return echartsBase({
      tooltip: { trigger: 'axis' },
      grid: chartGrid(bottom),
      xAxis: { ...categoryAxis(years.length > 12 ? 35 : 0), data: years },
      yAxis: valueAxis(),
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
    });
  }

  const series = qKeys.map((q) => ({
    name: q,
    type: 'bar' as const,
    stack: 'yearQ',
    emphasis: { focus: 'series' as const },
    data: years.map((y) => yq[y]?.[q] ?? 0),
    itemStyle: { color: quartileSectorColor(q) },
  }));

  return echartsBase({
    tooltip: { trigger: 'axis' },
    legend: { type: 'scroll', bottom: 0, textStyle: { color: CHART_COLORS.muted } },
    grid: chartGrid(bottom),
    xAxis: { ...categoryAxis(years.length > 12 ? 35 : 0), data: years },
    yAxis: valueAxis(),
    series,
  });
});

const quartileOption = computed(() => {
  const s = props.stats;
  if (!s || !Object.keys(s.quartile_counts).length) {
    return echartsBase({
      title: {
        text: '暂无分区数据',
        left: 'center',
        top: 'middle',
        textStyle: { color: CHART_COLORS.muted, fontSize: 14 },
      },
    });
  }
  const entries = Object.entries(s.quartile_counts);
  const total = entries.reduce((sum, [, v]) => sum + v, 0);
  const data = entries.map(([name, value]) => ({
    name,
    value,
    itemStyle: {
      color: quartileSectorColor(name),
      opacity: props.activeQuartile && props.activeQuartile !== name ? 0.35 : 1,
    },
  }));
  return echartsBase({
    tooltip: {
      trigger: 'item',
      formatter: (p: { name: string; value: number; percent?: number }) => {
        const pct = p.percent != null ? p.percent.toFixed(1) : ((p.value / total) * 100).toFixed(1);
        return `${p.name}: ${p.value} 篇 (${pct}%)`;
      },
    },
    legend: { bottom: 0, textStyle: { color: CHART_COLORS.muted } },
    series: [
      {
        type: 'pie',
        radius: ['36%', '62%'],
        data,
        label: {
          color: CHART_COLORS.text,
          formatter: '{b}\n{d}%',
        },
        emphasis: {
          scale: true,
          scaleSize: 8,
        },
      },
    ],
  });
});

const journalOption = computed(() => {
  const rows = journals.value;
  if (!rows.length) {
    return echartsBase({
      title: {
        text: '暂无期刊数据',
        left: 'center',
        top: 'middle',
        textStyle: { color: CHART_COLORS.muted, fontSize: 14 },
      },
    });
  }
  const names = rows.map((r) => r.name).reverse();
  const counts = rows.map((r) => r.count).reverse();
  const dz = dataZoomForJournals(names.length);
  const gridLeft = 8;
  const gridRight = dz.length ? 36 : 16;
  return echartsBase({
    tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
    grid: { left: gridLeft, right: gridRight, top: 16, bottom: 24, containLabel: true },
    dataZoom: dz,
    xAxis: valueAxis('篇数'),
    yAxis: {
      type: 'category',
      data: names,
      axisLine: { lineStyle: { color: CHART_COLORS.axis } },
      axisLabel: { color: CHART_COLORS.muted, width: 120, overflow: 'truncate' },
    },
    series: [
      {
        type: 'bar',
        data: counts,
        itemStyle: {
          color: {
            type: 'linear',
            x: 0,
            y: 0,
            x2: 1,
            y2: 0,
            colorStops: [
              { offset: 0, color: '#00897b' },
              { offset: 1, color: '#00695c' },
            ],
          },
        },
      },
    ],
  });
});

const ifOption = computed(() => {
  const bins = ifBins.value;
  if (!bins.length) {
    return echartsBase({
      title: {
        text: '暂无影响因子数据',
        left: 'center',
        top: 'middle',
        textStyle: { color: CHART_COLORS.muted, fontSize: 14 },
      },
    });
  }
  const total = bins.reduce((s, b) => s + b.count, 0);
  const labels = bins.map((b) => b.range);
  const counts = bins.map((b) => b.count);
  return echartsBase({
    tooltip: {
      trigger: 'axis',
      formatter: (params: { name: string; value: number } | { name: string; value: number }[]) => {
        const p = Array.isArray(params) ? params[0] : params;
        if (!p) return '';
        const pct = total ? ((p.value / total) * 100).toFixed(1) : '0';
        return `${p.name}<br/>${p.value} 篇 (${pct}%)`;
      },
    },
    grid: chartGrid(40),
    xAxis: { ...categoryAxis(30), data: labels },
    yAxis: valueAxis(),
    series: [
      {
        type: 'bar',
        data: counts,
        itemStyle: { color: '#3949ab' },
      },
    ],
  });
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

function onPieClick(params: { name?: string; componentType?: string }) {
  if (params.componentType !== 'series' || !params.name) {
    return;
  }
  const next = props.activeQuartile === params.name ? null : params.name;
  emit('quartile-select', next);
}

function onYearRangeFromBar(range: [number, number] | null) {
  emit('year-range', range);
}
</script>

<template>
  <div v-if="stats" class="stats">
    <section class="cards">
      <div class="card panel">
        <span class="card-accent" />
        <span class="label">检索命中</span>
        <strong>{{ stats.total_hits }}</strong>
      </div>
      <div class="card panel">
        <span class="card-accent" />
        <span class="label">本次分析</span>
        <strong>{{ stats.analyzed_count }}</strong>
        <span v-if="hasActiveFilters && analyzedTotal != null" class="card-sub">
          当前视图 {{ articles.length }} / {{ analyzedTotal }} 篇
        </span>
      </div>
      <div class="card panel" :class="{ warn: matchRateWarning }">
        <span class="card-accent" :class="{ warn: matchRateWarning }" />
        <span class="label">期刊匹配率</span>
        <strong>{{ (stats.journal_match_rate * 100).toFixed(1) }}%</strong>
      </div>
      <div class="card panel">
        <span class="card-accent" />
        <span class="label">摘要覆盖率</span>
        <strong>{{ (coverage.rate * 100).toFixed(1) }}%</strong>
        <span class="card-sub">{{ coverage.withAbstract }} / {{ coverage.total }}</span>
      </div>
    </section>
    <div v-if="ifText" class="if-box panel">
      <span class="if-title">影响因子（已匹配 {{ ifText.n }} 篇）</span>
      <span v-if="ifText.n === 0" class="muted">无匹配期刊，无法计算 IF 统计。</span>
      <template v-else>
        均值 {{ ifText.mean?.toFixed(2) ?? '—' }} · 中位数
        {{ ifText.median?.toFixed(2) ?? '—' }} · 最小
        {{ ifText.min?.toFixed(2) ?? '—' }} · 最大 {{ ifText.max?.toFixed(2) ?? '—' }}
      </template>
    </div>
    <YearRangeBar
      :years="sortedYears"
      :model-value="yearRange ?? null"
      @year-range="onYearRangeFromBar"
    />
    <p v-if="activeQuartile" class="chart-hint muted">
      已选分区：{{ activeQuartile }}（再次点击饼图扇区可取消）
    </p>
    <div class="charts">
      <div class="chart-wrap panel">
        <h3 class="chart-title">年份分布（按分区堆积）</h3>
        <p class="chart-sub muted">使用上方年份条筛选区间</p>
        <v-chart class="chart" :option="yearOption" autoresize />
      </div>
      <div class="chart-wrap panel">
        <h3 class="chart-title">分区分布</h3>
        <p class="chart-sub muted">点击扇区筛选表格与副图</p>
        <v-chart class="chart" :option="quartileOption" autoresize @click="onPieClick" />
      </div>
      <div class="chart-wrap panel">
        <h3 class="chart-title">期刊 Top {{ journals.length || 12 }}</h3>
        <p v-if="hasActiveFilters" class="chart-sub muted">基于当前筛选语料</p>
        <v-chart class="chart chart-tall" :option="journalOption" autoresize />
      </div>
      <div class="chart-wrap panel">
        <h3 class="chart-title">影响因子分布</h3>
        <p v-if="hasActiveFilters" class="chart-sub muted">基于当前筛选语料</p>
        <v-chart class="chart" :option="ifOption" autoresize />
      </div>
    </div>
  </div>
  <p v-else class="muted">暂无统计数据。</p>
</template>

<style scoped lang="scss">
.stats {
  display: flex;
  flex-direction: column;
  gap: var(--space-md);
}

.cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: var(--space-sm);
}

.card {
  position: relative;
  padding: 0.85rem 1rem 0.85rem 1.15rem;
  display: flex;
  flex-direction: column;
  gap: 0.2rem;
  overflow: hidden;

  &.warn strong {
    color: var(--warning);
  }
}

.card-accent {
  position: absolute;
  left: 0;
  top: 0;
  bottom: 0;
  width: 4px;
  background: var(--accent);

  &.warn {
    background: var(--warning);
  }
}

.label {
  font-size: var(--text-xs);
  color: var(--muted);
}

strong {
  font-size: 1.35rem;
  font-variant-numeric: tabular-nums;
  color: var(--text);
}

.card-sub {
  font-size: var(--text-xs);
  color: var(--muted);
}

.if-box {
  font-size: 0.88rem;
  line-height: 1.5;
  padding: 0.65rem 0.85rem;
}

.if-title {
  display: block;
  font-weight: 600;
  margin-bottom: 0.35rem;
  color: var(--text);
}

.chart-hint {
  margin: 0;
  font-size: var(--text-sm);
}

.muted {
  color: var(--muted);
}

.charts {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: var(--space-md);
}

.chart-wrap {
  padding: 0.55rem 0.5rem 0.35rem;
}

.chart-title {
  margin: 0 0 0.15rem 0.4rem;
  font-size: 0.9rem;
  font-weight: 600;
  color: var(--text);
}

.chart-sub {
  margin: 0 0 0.25rem 0.4rem;
  font-size: var(--text-xs);
}

.chart {
  height: 280px;
  width: 100%;
}

.chart-tall {
  height: 320px;
}
</style>
