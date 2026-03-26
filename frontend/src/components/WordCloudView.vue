<script setup lang="ts">
import WordCloud from 'wordcloud';
import { nextTick, onBeforeUnmount, ref, watch } from 'vue';

import type { WordCloudItem } from '@/api/analyze';
import { wordcloudColor } from '@/utils/chartPalette';

const props = defineProps<{
  items: WordCloudItem[];
}>();

const canvasRef = ref<HTMLCanvasElement | null>(null);
let ro: ResizeObserver | null = null;

function draw() {
  const el = canvasRef.value;
  if (!el || !props.items.length) {
    return;
  }
  const parent = el.parentElement;
  if (parent) {
    el.width = parent.clientWidth;
    // 更高画布，词云区域更大
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
  });
}

watch(
  () => props.items,
  () => {
    nextTick(() => draw());
  },
  { deep: true },
);

watch(canvasRef, (el) => {
  if (el?.parentElement) {
    ro?.disconnect();
    ro = new ResizeObserver(() => draw());
    ro.observe(el.parentElement);
  }
});

onBeforeUnmount(() => {
  ro?.disconnect();
});
</script>

<template>
  <div class="wc">
    <p v-if="!items.length" class="muted">暂无词频数据（或摘要过少）。</p>
    <div v-else class="canvas-wrap">
      <canvas ref="canvasRef" class="canvas" />
    </div>
  </div>
</template>

<style scoped lang="scss">
.wc {
  min-height: 320px;
  padding: 0.75rem;
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: var(--radius);
}

.canvas-wrap {
  width: 100%;
}

.canvas {
  display: block;
  width: 100%;
  height: auto;
}

.muted {
  color: var(--muted);
  font-size: 0.9rem;
}
</style>
