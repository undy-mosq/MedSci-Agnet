<!-- [2026-05-18] 图表区顶部公共年份双端拉条，与 useDashboardFilters 同步。 -->
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

const maxIdx = computed(() => Math.max(0, props.years.length - 1));

const labelText = computed(() => {
  if (!props.years.length) {
    return '';
  }
  const i0 = Math.min(startIdx.value, endIdx.value);
  const i1 = Math.max(startIdx.value, endIdx.value);
  return `${props.years[i0]} – ${props.years[i1]}`;
});

const isFullRange = computed(
  () => startIdx.value === 0 && endIdx.value === maxIdx.value && maxIdx.value > 0,
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
  const i0 = Math.min(startIdx.value, endIdx.value);
  const i1 = Math.max(startIdx.value, endIdx.value);
  if (i0 === 0 && i1 === maxIdx.value) {
    emit('year-range', null);
    return;
  }
  const y0 = parseInt(props.years[i0]!, 10);
  const y1 = parseInt(props.years[i1]!, 10);
  if (Number.isFinite(y0) && Number.isFinite(y1)) {
    emit('year-range', [Math.min(y0, y1), Math.max(y0, y1)]);
  }
}

function onStartInput(ev: Event) {
  const v = parseInt((ev.target as HTMLInputElement).value, 10);
  startIdx.value = v;
  if (startIdx.value > endIdx.value) {
    endIdx.value = startIdx.value;
  }
  emitRange();
}

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
    <div class="bar-sliders">
      <label class="slider-label">
        <span class="sr-only">起始年份</span>
        <input
          type="range"
          class="range range-start"
          :min="0"
          :max="maxIdx"
          :value="startIdx"
          @input="onStartInput"
        />
      </label>
      <label class="slider-label">
        <span class="sr-only">结束年份</span>
        <input
          type="range"
          class="range range-end"
          :min="0"
          :max="maxIdx"
          :value="endIdx"
          @input="onEndInput"
        />
      </label>
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
  margin-bottom: 0.5rem;
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

.bar-sliders {
  position: relative;
  padding: 0.25rem 0 1.25rem;
}

.slider-label {
  display: block;
  margin: 0.15rem 0;
}

.range {
  width: 100%;
  height: 6px;
  accent-color: var(--accent);
  cursor: pointer;
}

.tick-labels {
  display: flex;
  justify-content: space-between;
  font-size: var(--text-xs);
  color: var(--muted);
  margin-top: 0.15rem;
}

.sr-only {
  position: absolute;
  width: 1px;
  height: 1px;
  padding: 0;
  margin: -1px;
  overflow: hidden;
  clip: rect(0, 0, 0, 0);
  border: 0;
}

.muted {
  color: var(--muted);
}
</style>
