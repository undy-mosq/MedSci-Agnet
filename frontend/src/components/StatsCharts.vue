<!-- [2026-05-18] 年份公共拉条置顶；移除年份图 dataZoom。 -->
<!-- [2026-05-19] yearOption 按 yearRange 裁剪 X 轴，计数仍用全库 stats。 -->
<!-- [2026-05-19] 图表 2×2 网格；期刊 Top12 点击展示指标详情。 -->
<!-- [2026-05-19] 期刊选中仅在 Top12 名单变化时清空，MedSci 补全保留选中。 -->
<!-- [2026-05-19] 第二行期刊/IF 图下沿对齐；IF 改为数值轴直方图。 -->
<script setup lang="ts">
import { computed, ref, watch } from 'vue';

import type { ArticleItem, CorpusStats } from '@/api/analyze';
import YearRangeBar from '@/components/YearRangeBar.vue';
import {
  abstractCoverage,
  ifHistogram,
  journalDetailForName,
  topJournals,
} from '@/utils/articleAggregates';
import { displayQuartile } from '@/utils/quartileDisplay';
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
const ifHist = computed(() => ifHistogram(props.articles, 8));
const selectedJournal = ref<string | null>(null);

/** 函数功能：Top12 期刊名序列，用于判断选中是否应清空。
 *  输入说明：无（读 props.articles）。
 *  输出说明：换行拼接的期刊名字符串。 */
function journalTop12Fingerprint(): string {
  return topJournals(props.articles, 12)
    .map((j) => j.name)
    .join('\n');
}

watch(
  () => journalTop12Fingerprint(),
  (next, prev) => {
    if (!prev) {
      return;
    }
    if (next !== prev) {
      selectedJournal.value = null;
      return;
    }
    const sel = selectedJournal.value;
    if (sel && !next.split('\n').includes(sel)) {
      selectedJournal.value = null;
    }
  },
);

const journalDetail = computed(() => {
  const name = selectedJournal.value;
  if (!name) {
    return null;
  }
  return journalDetailForName(props.articles, name);
});

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

/** 函数功能：按年份条区间裁剪年份分布图 X 轴年份列表。
 *  输入说明：依赖 sortedYears 与 props.yearRange。
 *  输出说明：用于 yearOption 的年份字符串数组。 */
const chartYears = computed(() => {
  const all = sortedYears.value;
  const range = props.yearRange;
  if (range == null) {
    return all;
  }
  const [y0, y1] = range;
  return all.filter((y) => {
    const n = parseInt(y, 10);
    return Number.isFinite(n) && n >= y0 && n <= y1;
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
  const years = chartYears.value;
  if (!years.length) {
    return echartsBase({
      title: {
        text: '暂无年份数据',
        left: 'center',
        top: 'middle',
        textStyle: { color: CHART_COLORS.muted, fontSize: 14 },
      },
    });
  }
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
  const sel = selectedJournal.value;
  const barData = names.map((name, i) => {
    const base = {
      type: 'linear' as const,
      x: 0,
      y: 0,
      x2: 1,
      y2: 0,
      colorStops: [
        { offset: 0, color: '#00897b' },
        { offset: 1, color: '#00695c' },
      ],
    };
    if (sel === name) {
      return {
        value: counts[i],
        itemStyle: {
          color: {
            type: 'linear' as const,
            x: 0,
            y: 0,
            x2: 1,
            y2: 0,
            colorStops: [
              { offset: 0, color: '#00695c' },
              { offset: 1, color: '#004d40' },
            ],
          },
          borderColor: '#004d40',
          borderWidth: 2,
        },
      };
    }
    return {
      value: counts[i],
      itemStyle: { color: base },
    };
  });
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
        data: barData,
      },
    ],
  });
});

const ifOption = computed(() => {
  const hist = ifHist.value;
  if (!hist || !hist.bins.length) {
    return echartsBase({
      title: {
        text: '暂无影响因子数据',
        left: 'center',
        top: 'middle',
        textStyle: { color: CHART_COLORS.muted, fontSize: 14 },
      },
    });
  }
  const { bins, step, domainMin, domainMax } = hist;
  const total = bins.reduce((s, b) => s + b.count, 0);
  const span = domainMax - domainMin;
  const barWidth =
    step > 0 ? step * 0.92 : Math.max(span * 0.35, 0.08);
  return echartsBase({
    tooltip: {
      trigger: 'axis',
      axisPointer: { type: 'shadow' },
      formatter: (
        params:
          | { dataIndex?: number; value?: number | [number, number] }
          | { dataIndex?: number; value?: number | [number, number] }[],
      ) => {
        const p = Array.isArray(params) ? params[0] : params;
        if (!p || p.dataIndex == null) {
          return '';
        }
        const bin = bins[p.dataIndex];
        if (!bin) {
          return '';
        }
        const count = Array.isArray(p.value) ? p.value[1] : (p.value as number);
        const pct = total ? ((count / total) * 100).toFixed(1) : '0';
        return `${bin.range}<br/>${count} 篇 (${pct}%)`;
      },
    },
    grid: chartGrid(44),
    xAxis: {
      type: 'value',
      name: '影响因子',
      min: domainMin,
      max: domainMax,
      nameTextStyle: { color: CHART_COLORS.muted },
      axisLine: { lineStyle: { color: CHART_COLORS.axis } },
      axisLabel: {
        color: CHART_COLORS.muted,
        formatter: (v: number) => (Number.isFinite(v) ? v.toFixed(1) : ''),
      },
      splitLine: { lineStyle: { color: CHART_COLORS.split } },
    },
    yAxis: valueAxis(),
    series: [
      {
        type: 'bar',
        data: bins.map((b) => [(b.min + b.max) / 2, b.count]),
        barWidth,
        itemStyle: { color: '#3949ab', borderRadius: 0 },
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

/** 函数功能：期刊柱状图点击展示/取消详情。
 *  输入说明：ECharts 点击事件 params。
 *  输出说明：无。 */
function onJournalBarClick(params: { name?: string; componentType?: string }) {
  if (params.componentType !== 'series' || !params.name) {
    return;
  }
  const next = selectedJournal.value === params.name ? null : params.name;
  selectedJournal.value = next;
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
        <p class="chart-sub muted">拖动上方年份条限定 X 轴区间（计数为全库）</p>
        <v-chart class="chart" :option="yearOption" autoresize />
      </div>
      <div class="chart-wrap panel">
        <h3 class="chart-title">分区分布</h3>
        <p class="chart-sub muted">点击扇区筛选表格与副图</p>
        <v-chart class="chart" :option="quartileOption" autoresize @click="onPieClick" />
      </div>
      <div
        class="chart-wrap panel chart-wrap-row2 chart-wrap-journal"
        :class="{ 'chart-meta-filter': hasActiveFilters }"
      >
        <div class="chart-row2-body">
          <div class="chart-meta">
            <h3 class="chart-title">期刊 Top {{ journals.length || 12 }}</h3>
            <p class="chart-sub muted">点击期刊条查看指标（再次点击可取消）</p>
            <p v-if="hasActiveFilters" class="chart-sub muted">基于当前筛选语料</p>
            <p v-else class="chart-sub chart-sub-spacer" aria-hidden="true">&nbsp;</p>
          </div>
          <div class="chart-plot">
            <v-chart
              class="chart chart-row2"
              :option="journalOption"
              autoresize
              @click="onJournalBarClick"
            />
          </div>
        </div>
        <div v-if="journalDetail" class="journal-detail panel">
          <p class="journal-detail-title">{{ journalDetail.name }}</p>
          <dl class="journal-detail-grid">
            <dt>本语料篇数</dt>
            <dd>{{ journalDetail.count }}</dd>
            <dt>ISSN</dt>
            <dd>{{ journalDetail.issn ?? '—' }}</dd>
            <dt>影响因子</dt>
            <dd>{{ journalDetail.impact_factor?.toFixed(2) ?? '—' }}</dd>
            <dt>分区</dt>
            <dd>{{ displayQuartile(journalDetail.quartile) }}</dd>
          </dl>
        </div>
      </div>
      <div
        class="chart-wrap panel chart-wrap-row2"
        :class="{ 'chart-meta-filter': hasActiveFilters }"
      >
        <div class="chart-row2-body">
          <div class="chart-meta">
            <h3 class="chart-title">影响因子分布</h3>
            <p class="chart-sub chart-sub-spacer" aria-hidden="true">&nbsp;</p>
            <p v-if="hasActiveFilters" class="chart-sub muted">基于当前筛选语料</p>
            <p v-else class="chart-sub chart-sub-spacer" aria-hidden="true">&nbsp;</p>
          </div>
          <div class="chart-plot">
            <v-chart class="chart chart-row2" :option="ifOption" autoresize />
          </div>
        </div>
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
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: var(--space-md);
}

@media (max-width: 720px) {
  .charts {
    grid-template-columns: 1fr;
  }
}

.chart-wrap-row2 {
  display: flex;
  flex-direction: column;
  height: 100%;
  gap: var(--space-sm);
}

.chart-row2-body {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-height: 0;
}

.chart-meta {
  flex-shrink: 0;
  min-height: 4.35rem;
}

.chart-meta-filter .chart-meta {
  min-height: 5.05rem;
}

.chart-sub-spacer {
  visibility: hidden;
  margin: 0 0 0.25rem 0.4rem;
  min-height: 1em;
}

.chart-plot {
  flex: 1;
  display: flex;
  flex-direction: column;
  justify-content: flex-end;
  flex-shrink: 0;
  min-height: 320px;
}

.journal-detail {
  margin: 0 0.4rem 0.25rem;
  padding: 0.55rem 0.65rem;
  font-size: var(--text-sm);
}

.journal-detail-title {
  margin: 0 0 0.4rem;
  font-weight: 600;
  font-size: 0.88rem;
  color: var(--text);
}

.journal-detail-grid {
  display: grid;
  grid-template-columns: auto 1fr;
  gap: 0.25rem 0.75rem;
  margin: 0;

  dt {
    margin: 0;
    color: var(--muted);
    font-weight: 500;
  }

  dd {
    margin: 0;
    font-variant-numeric: tabular-nums;
    color: var(--text);
  }
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

.chart-row2 {
  height: 320px;
}
</style>
