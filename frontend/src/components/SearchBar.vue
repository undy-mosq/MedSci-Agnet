<script setup lang="ts">
import { ref, watch } from 'vue';

const props = defineProps<{
  loading: boolean;
  initialQuery?: string;
}>();

const emit = defineEmits<{
  search: [query: string];
}>();

const query = ref(props.initialQuery ?? 'cancer immunotherapy');

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
  emit('search', q);
}
</script>

<template>
  <header class="search-bar">
    <h1 class="title">检索</h1>
    <p class="hint">
      数据来自 NCBI E-utilities；影响因子与 JCR 分区来自本地映射表
      <code>data/journal_metrics.json</code>，未命中期刊显示为未知。每次分析固定检索
      <strong>100</strong> 条文献。
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
      <button class="btn" type="submit" :disabled="loading || !query.trim()">
        {{ loading ? '检索中…' : '分析' }}
      </button>
    </form>
  </header>
</template>

<style scoped lang="scss">
.search-bar {
  margin-bottom: 0.25rem;
  padding: 1rem 1.1rem;
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: var(--radius);
}

.title {
  margin: 0 0 0.5rem;
  font-size: 1.15rem;
  font-weight: 600;
  color: var(--text);
}

.hint {
  margin: 0 0 1rem;
  font-size: 0.82rem;
  color: var(--muted);
  line-height: 1.55;
}

code {
  font-size: 0.88em;
  background: var(--surface-elevated);
  padding: 0.12em 0.35em;
  border-radius: 3px;
  border: 1px solid var(--border);
}

.row {
  display: flex;
  flex-wrap: wrap;
  gap: 0.65rem;
  align-items: stretch;
}

.input {
  flex: 1 1 220px;
  min-width: 0;
  padding: 0.55rem 0.75rem;
  border-radius: var(--radius-sm);
  border: 1px solid var(--border);
  background: #fff;
  color: var(--text);
  font-size: 0.95rem;

  &:focus {
    outline: 2px solid var(--accent);
    outline-offset: 0;
  }
}

.btn {
  padding: 0.55rem 1.35rem;
  border: 1px solid var(--accent);
  border-radius: var(--radius-sm);
  background: var(--accent);
  color: #fff;
  font-weight: 600;
  font-size: 0.95rem;
  cursor: pointer;

  &:hover:not(:disabled) {
    background: var(--accent-hover);
    border-color: var(--accent-hover);
  }

  &:disabled {
    opacity: 0.55;
    cursor: not-allowed;
  }
}
</style>
