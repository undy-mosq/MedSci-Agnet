<!-- [2026-05-18] 单轨道双拇指年份区间拉条。 -->
<script setup lang="ts">
import { computed, ref, watch } from 'vue';

const props = defineProps<{
  years: string[];
  modelValue: [number, number] | null;
}>();

const emit = defineEmits<{
  'year-range': [range: [number, number] | null];
}>();

const startIdx = ref(0);
const endIdx = ref(0);
const activeThumb = ref<'start' | 'end'>('end');

const maxIdx = computed(() => Math.max(0, props.years.length - 1));

const lowIdx = computed(() => Math.min(startIdx.value, endIdx.value));
const highIdx = computed(() => Math.max(startIdx.value, endIdx.value));

const fillStyle = computed(() => {
  if (maxIdx.value <= 0) {
    return { left: '0%', width: '100%' };
  }
  const left = (lowIdx.value / maxIdx.value) * 100;
  const right = (highIdx.value / maxIdx.value) * 100;
  return {
    left: `${left}%`,
    width: `${right - left}%`,
  };
});

const labelText = computed(() => {
  if (!props.years.length) {
    return '';
  }
  return `${props.years[lowIdx.value]} – ${props.years[highIdx.value]}`;
});

const isFullRange = computed(
  () => lowIdx.value === 0 && highIdx.value === maxIdx.value && maxIdx.value > 0,
);

/** 函数功能：将 modelValue 同步到拉条索引。
 *  输入说明：range 为年份区间或 null（全年份）。
 *  输出说明：无。 */
function applyModelValue(range: [number, number] | null) {
  if (!props.years.length) {
    return;
  }
  if (range == null) {
    startIdx.value = 0;
    endIdx.value = maxIdx.value;
    return;
  }
  const [y0, y1] = range;
  let i0 = props.years.findIndex((s) => {
    const y = parseInt(s, 10);
    return Number.isFinite(y) && y >= y0;
  });
  if (i0 < 0) {
    i0 = 0;
  }
  let i1 = -1;
  for (let i = props.years.length - 1; i >= 0; i--) {
    const y = parseInt(props.years[i]!, 10);
    if (Number.isFinite(y) && y <= y1) {
      i1 = i;
      break;
    }
  }
  if (i1 < 0) {
    i1 = maxIdx.value;
  }
  startIdx.value = Math.min(i0, i1);
  endIdx.value = Math.max(i0, i1);
}

/** 函数功能：根据当前索引向父组件发出年份筛选。
 *  输入说明：无。
 *  输出说明：无。 */
function emitRange() {
  if (!props.years.length) {
    return;
  }
  if (lowIdx.value === 0 && highIdx.value === maxIdx.value) {
    emit('year-range', null);
    return;
  }
  const y0 = parseInt(props.years[lowIdx.value]!, 10);
  const y1 = parseInt(props.years[highIdx.value]!, 10);
  if (Number.isFinite(y0) && Number.isFinite(y1)) {
    emit('year-range', [Math.min(y0, y1), Math.max(y0, y1)]);
  }
}

/** 函数功能：拖动起始拇指并约束区间。
 *  输入说明：ev 为 range input 事件。
 *  输出说明：无。 */
function onStartInput(ev: Event) {
  const v = parseInt((ev.target as HTMLInputElement).value, 10);
  startIdx.value = v;
  if (startIdx.value > endIdx.value) {
    endIdx.value = startIdx.value;
  }
  emitRange();
}

/** 函数功能：拖动结束拇指并约束区间。
 *  输入说明：ev 为 range input 事件。
 *  输出说明：无。 */
function onEndInput(ev: Event) {
  const v = parseInt((ev.target as HTMLInputElement).value, 10);
  endIdx.value = v;
  if (endIdx.value < startIdx.value) {
    startIdx.value = endIdx.value;
  }
  emitRange();
}

watch(
  () => props.years,
  () => {
    startIdx.value = 0;
    endIdx.value = maxIdx.value;
    applyModelValue(props.modelValue);
  },
  { immediate: true },
);

watch(
  () => props.modelValue,
  (v) => {
    applyModelValue(v);
  },
);
</script>

<template>
  <div
    v-if="years.length >= 2"
    class="year-range-bar panel"
    role="group"
    aria-label="年份区间筛选"
  >
    <div class="bar-head">
      <span class="bar-title">年份筛选</span>
      <span class="bar-value" :class="{ muted: isFullRange }">{{ labelText }}</span>
      <span v-if="isFullRange" class="bar-hint muted">（全部年份）</span>
    </div>
    <div class="dual-range">
      <div class="track">
        <div class="track-fill" :style="fillStyle" />
      </div>
      <input
        type="range"
        class="thumb thumb-start"
        :class="{ 'thumb-active': activeThumb === 'start' }"
        :min="0"
        :max="maxIdx"
        :value="startIdx"
        aria-label="起始年份"
        @pointerdown="activeThumb = 'start'"
        @input="onStartInput"
      />
      <input
        type="range"
        class="thumb thumb-end"
        :class="{ 'thumb-active': activeThumb === 'end' }"
        :min="0"
        :max="maxIdx"
        :value="endIdx"
        aria-label="结束年份"
        @pointerdown="activeThumb = 'end'"
        @input="onEndInput"
      />
      <div class="tick-labels">
        <span>{{ years[0] }}</span>
        <span>{{ years[maxIdx] }}</span>
      </div>
    </div>
  </div>
</template>

<style scoped lang="scss">
.year-range-bar {
  padding: 0.65rem 0.85rem;
}

.bar-head {
  display: flex;
  flex-wrap: wrap;
  align-items: baseline;
  gap: 0.35rem 0.65rem;
  margin-bottom: 0.55rem;
}

.bar-title {
  font-size: var(--text-sm);
  font-weight: 600;
  color: var(--text);
}

.bar-value {
  font-size: var(--text-sm);
  font-variant-numeric: tabular-nums;
  color: var(--accent);
  font-weight: 600;

  &.muted {
    color: var(--muted);
    font-weight: 500;
  }
}

.bar-hint {
  font-size: var(--text-xs);
}

.dual-range {
  position: relative;
  height: 28px;
  margin: 0 2px 1.1rem;
}

.track {
  position: absolute;
  left: 0;
  right: 0;
  top: 50%;
  transform: translateY(-50%);
  height: 6px;
  border-radius: 3px;
  background: var(--border);
  pointer-events: none;
}

.track-fill {
  position: absolute;
  top: 0;
  height: 100%;
  border-radius: 3px;
  background: var(--accent);
}

.thumb {
  position: absolute;
  left: 0;
  width: 100%;
  height: 28px;
  margin: 0;
  padding: 0;
  background: transparent;
  pointer-events: none;
  -webkit-appearance: none;
  appearance: none;

  &::-webkit-slider-runnable-track {
    height: 6px;
    background: transparent;
    border: none;
  }

  &::-moz-range-track {
    height: 6px;
    background: transparent;
    border: none;
  }

  &::-webkit-slider-thumb {
    -webkit-appearance: none;
    pointer-events: auto;
    width: 16px;
    height: 16px;
    margin-top: -5px;
    border-radius: 50%;
    border: 2px solid #fff;
    background: var(--accent);
    box-shadow: 0 1px 4px rgba(38, 50, 56, 0.25);
    cursor: grab;
  }

  &::-moz-range-thumb {
    pointer-events: auto;
    width: 16px;
    height: 16px;
    border-radius: 50%;
    border: 2px solid #fff;
    background: var(--accent);
    box-shadow: 0 1px 4px rgba(38, 50, 56, 0.25);
    cursor: grab;
  }

  &.thumb-active {
    z-index: 3;
  }

  &.thumb-start {
    z-index: 1;
  }

  &.thumb-end {
    z-index: 2;
  }
}

.tick-labels {
  position: absolute;
  left: 0;
  right: 0;
  bottom: -1.1rem;
  display: flex;
  justify-content: space-between;
  font-size: var(--text-xs);
  color: var(--muted);
  pointer-events: none;
}

.muted {
  color: var(--muted);
}
</style>
