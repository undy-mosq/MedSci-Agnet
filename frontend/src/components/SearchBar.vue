<script setup lang="ts">
import { ref, watch } from 'vue';

const props = defineProps<{
  loading: boolean;
  initialQuery?: string;
  initialMax?: number;
}>();

const emit = defineEmits<{
  search: [query: string, maxResults: number];
}>();

const query = ref(props.initialQuery ?? 'cancer immunotherapy');
const maxResults = ref(props.initialMax ?? 50);

watch(
  () => props.initialQuery,
  (v) => {
    if (v !== undefined) {
      query.value = v;
    }
  },
);

function onSubmit() {
  const q = query.value.trim();
  if (!q || props.loading) {
    return;
  }
  const cap = Math.min(200, Math.max(1, maxResults.value));
  emit('search', q, cap);
}
</script>

<template>
  <header class="search-bar">
    <h1 class="title">PubMed 文献分析</h1>
    <p class="hint">
      数据来自 NCBI E-utilities；影响因子与 JCR 分区来自本地映射表
      <code>data/journal_metrics.json</code>，未命中期刊显示为未知。
    </p>
    <form class="row" @submit.prevent="onSubmit">
      <input
        v-model="query"
        class="input"
        type="search"
        placeholder="输入 PubMed 检索式，如 cancer AND therapy"
        :disabled="loading"
        autocomplete="off"
      />
      <label class="max-label">
        条数
        <input
          v-model.number="maxResults"
          class="input max"
          type="number"
          min="1"
          max="200"
          :disabled="loading"
        />
      </label>
      <button class="btn" type="submit" :disabled="loading || !query.trim()">
        {{ loading ? '检索中…' : '分析' }}
      </button>
    </form>
  </header>
</template>

<style scoped lang="scss">
.search-bar {
  margin-bottom: 1.25rem;
}

.title {
  margin: 0 0 0.35rem;
  font-size: 1.5rem;
  font-weight: 650;
  letter-spacing: -0.02em;
}

.hint {
  margin: 0 0 1rem;
  font-size: 0.85rem;
  color: var(--muted);
  line-height: 1.45;
}

code {
  font-size: 0.8em;
  background: var(--surface);
  padding: 0.1em 0.35em;
  border-radius: 4px;
  border: 1px solid var(--border);
}

.row {
  display: flex;
  flex-wrap: wrap;
  gap: 0.65rem;
  align-items: center;
}

.input {
  flex: 1 1 220px;
  min-width: 0;
  padding: 0.55rem 0.75rem;
  border-radius: var(--radius);
  border: 1px solid var(--border);
  background: var(--surface);
  color: var(--text);
  font-size: 0.95rem;

  &:focus {
    outline: 2px solid var(--accent);
    outline-offset: 0;
  }
}

.max-label {
  display: flex;
  align-items: center;
  gap: 0.35rem;
  font-size: 0.85rem;
  color: var(--muted);
}

.max {
  width: 4.5rem;
  flex: none;
}

.btn {
  padding: 0.55rem 1.1rem;
  border: none;
  border-radius: var(--radius);
  background: linear-gradient(180deg, var(--accent), var(--accent-dim));
  color: #fff;
  font-weight: 600;
  cursor: pointer;

  &:disabled {
    opacity: 0.55;
    cursor: not-allowed;
  }
}
</style>
