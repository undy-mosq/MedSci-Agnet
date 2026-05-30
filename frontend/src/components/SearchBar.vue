<!-- [2026-05-18] 使用说明折叠、panel 样式、输入框 focus ring。 -->
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
  <header class="search-bar panel">
    <h1 class="title">检索</h1>
    <details class="usage-details">
      <summary>使用说明</summary>
      <p class="hint">
        数据来自 NCBI E-utilities；首轮使用
        <a
          class="link-map"
          href="/journal-metrics.html"
          target="_blank"
          rel="noopener noreferrer"
          >本地映射表</a
        >
        中的影响因子与中科院大类分区。未命中期刊将自动从 MedSci 补全（约 10
        本/批同步，其余后台增量更新）。每次分析固定检索
        <strong>500</strong> 条文献；综述（LLM）仅依据近 5 年高影响因子排序后的 Top100
        题录生成，与下方「近 5 年高影响因子文献」表一致。
      </p>
    </details>
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
  padding: var(--space-md) 1.1rem;
}

.title {
  margin: 0 0 var(--space-sm);
  font-size: var(--text-xl);
  font-weight: 600;
  color: var(--text);
}

.usage-details {
  margin: 0 0 var(--space-md);
  font-size: var(--text-sm);

  summary {
    cursor: pointer;
    color: var(--accent);
    font-weight: 600;
    user-select: none;

    &:hover {
      text-decoration: underline;
    }
  }
}

.hint {
  margin: var(--space-sm) 0 0;
  color: var(--muted);
  line-height: 1.55;
}

.link-map {
  color: var(--accent);
  font-weight: 600;
  text-decoration: none;

  &:hover {
    text-decoration: underline;
  }
}

.row {
  display: flex;
  flex-wrap: wrap;
  gap: var(--space-sm);
  align-items: stretch;
}

.input {
  flex: 1 1 220px;
  min-width: 0;
  padding: 0.6rem 0.85rem;
  border-radius: var(--radius-sm);
  border: 1px solid var(--border);
  background: #fff;
  color: var(--text);
  font-size: var(--text-base);
  transition: border-color var(--transition-fast), box-shadow var(--transition-fast);

  &:focus {
    outline: none;
    border-color: var(--accent);
    box-shadow: 0 0 0 3px var(--accent-soft);
  }
}

.btn {
  padding: 0.6rem 1.5rem;
  border: 1px solid var(--accent);
  border-radius: var(--radius-sm);
  background: var(--accent);
  color: #fff;
  font-weight: 600;
  font-size: var(--text-base);
  cursor: pointer;
  transition: background var(--transition-fast);

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
