<!-- [2026-05-18] 词云点击 emit、Top20 词条列表。 -->
<!-- [2026-05-19] 再次点击同一词取消高亮，emit null。 -->
<!-- [2026-05-19] 受控选中、词频指纹跳过重绘、Resize 防抖。 -->
<script setup lang="ts">
import WordCloud from 'wordcloud';
import { computed, nextTick, onBeforeUnmount, ref, watch } from 'vue';

import type { WordCloudItem } from '@/api/analyze';
import { wordcloudColor } from '@/utils/chartPalette';

const props = defineProps<{
  items: WordCloudItem[];
  selectedWord?: string | null;
}>();

const emit = defineEmits<{
  'word-click': [word: string | null];
}>();

const canvasRef = ref<HTMLCanvasElement | null>(null);
let ro: ResizeObserver | null = null;
let lastFingerprint = '';
let resizeTimer: ReturnType<typeof setTimeout> | null = null;

const topList = computed(() => {
  if (!props.items.length) {
    return [];
  }
  const total = props.items.reduce((s, w) => s + w.weight, 0);
  return [...props.items]
    .sort((a, b) => b.weight - a.weight)
    .slice(0, 20)
    .map((w) => ({
      word: w.word,
      weight: w.weight,
      pct: total ? ((w.weight / total) * 100).toFixed(1) : '0',
    }));
});

/** 函数功能：生成词云词频指纹，用于判断是否需要重绘 canvas。
 *  输入说明：items 为词云数据。
 *  输出说明：指纹字符串。 */
function wordcloudFingerprint(items: WordCloudItem[]): string {
  return items.map((w) => `${w.word}:${w.weight}`).join('|');
}

/** 函数功能：在 canvas 上绘制词云。
 *  输入说明：无（读 props.items）。
 *  输出说明：无。 */
function draw() {
  const el = canvasRef.value;
  if (!el || !props.items.length) {
    return;
  }
  const parent = el.parentElement;
  if (parent) {
    el.width = parent.clientWidth;
    el.height = Math.max(420, Math.floor(parent.clientWidth * 0.58));
  }
  const list: [string, number][] = props.items.map((w) => [w.word, w.weight]);
  const maxW = Math.max(...list.map((x) => x[1]), 1);
  WordCloud(el, {
    list,
    gridSize: 6,
    weightFactor: (size: number) => 16 + (size / maxW) * 56,
    fontFamily: 'Segoe UI, system-ui, sans-serif',
    color: (word: string) => wordcloudColor(word),
    rotateRatio: 0.15,
    backgroundColor: 'transparent',
    click: (item) => {
      if (item) {
        onWordSelect(item[0]);
      }
    },
  });
}

/** 函数功能：防抖触发词云重绘。
 *  输入说明：无。
 *  输出说明：无。 */
function scheduleDraw() {
  if (resizeTimer != null) {
    clearTimeout(resizeTimer);
  }
  resizeTimer = setTimeout(() => {
    resizeTimer = null;
    draw();
  }, 150);
}

/** 函数功能：词频变化时重绘；指纹不变则跳过。
 *  输入说明：items 为当前词云列表。
 *  输出说明：无。 */
function redrawIfFingerprintChanged(items: WordCloudItem[]) {
  const fp = wordcloudFingerprint(items);
  if (fp === lastFingerprint) {
    return;
  }
  lastFingerprint = fp;
  nextTick(() => draw());
}

/** 函数功能：选中或取消词条并通知父组件。
 *  输入说明：word 为词语文本。
 *  输出说明：无。 */
function onWordSelect(word: string) {
  if (props.selectedWord === word) {
    emit('word-click', null);
    return;
  }
  emit('word-click', word);
}

watch(
  () => props.items,
  (items) => {
    redrawIfFingerprintChanged(items);
  },
  { deep: true },
);

watch(canvasRef, (el) => {
  if (el?.parentElement) {
    ro?.disconnect();
    ro = new ResizeObserver(() => scheduleDraw());
    ro.observe(el.parentElement);
  }
});

onBeforeUnmount(() => {
  ro?.disconnect();
  if (resizeTimer != null) {
    clearTimeout(resizeTimer);
  }
});
</script>

<template>
  <div class="wc-layout">
    <div class="wc panel">
      <p v-if="!items.length" class="muted">暂无词频数据（或摘要过少）。</p>
      <div v-else class="canvas-wrap">
        <canvas ref="canvasRef" class="canvas" />
      </div>
    </div>
    <aside v-if="topList.length" class="word-list panel">
      <h3 class="list-title">高频词 Top 20</h3>
      <table class="list-table">
        <thead>
          <tr>
            <th>词</th>
            <th>篇数</th>
            <th>占比</th>
          </tr>
        </thead>
        <tbody>
          <tr
            v-for="row in topList"
            :key="row.word"
            :class="{ active: selectedWord === row.word }"
            @click="onWordSelect(row.word)"
          >
            <td>{{ row.word }}</td>
            <td class="num">{{ row.weight }}</td>
            <td class="num">{{ row.pct }}%</td>
          </tr>
        </tbody>
      </table>
    </aside>
  </div>
</template>

<style scoped lang="scss">
.wc-layout {
  display: grid;
  grid-template-columns: 1fr minmax(200px, 280px);
  gap: var(--space-sm);
  align-items: start;
}

@media (max-width: 720px) {
  .wc-layout {
    grid-template-columns: 1fr;
  }
}

.wc {
  min-height: 320px;
  padding: 0.75rem;
}

.canvas-wrap {
  width: 100%;
}

.canvas {
  display: block;
  width: 100%;
  height: auto;
  cursor: pointer;
}

.muted {
  color: var(--muted);
  font-size: 0.9rem;
}

.word-list {
  padding: 0.65rem 0.75rem;
}

.list-title {
  margin: 0 0 0.5rem;
  font-size: 0.9rem;
  font-weight: 600;
}

.list-table {
  width: 100%;
  border-collapse: collapse;
  font-size: var(--text-xs);

  th,
  td {
    padding: 0.3rem 0.35rem;
    text-align: left;
    border-bottom: 1px solid var(--border);
  }

  th {
    color: var(--muted);
    font-weight: 600;
  }

  tbody tr {
    cursor: pointer;

    &:hover td {
      background: var(--accent-soft);
    }

    &.active td {
      background: var(--row-highlight-bg);
      box-shadow: inset 0 0 0 1px var(--row-highlight-border);
      font-weight: 600;
    }
  }

  .num {
    font-variant-numeric: tabular-nums;
    text-align: right;
  }
}
</style>
