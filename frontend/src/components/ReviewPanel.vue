<script setup lang="ts">
import { computed } from 'vue';
import { marked } from 'marked';

import type { ReviewPayload } from '@/api/analyze';

const props = defineProps<{
  review: ReviewPayload | null;
  reviewLoading?: boolean;
  reviewError?: string | null;
}>();

const html = computed(() => {
  const t = props.review?.text;
  if (!t) {
    return '';
  }
  return marked.parse(t, { async: false }) as string;
});
</script>

<template>
  <div class="panel">
    <div v-if="reviewLoading && !review" class="skeleton" aria-busy="true">
      <div class="sk-line" />
      <div class="sk-line short" />
      <div class="sk-line" />
      <div class="sk-line mid" />
      <p class="sk-hint">正在生成综述…</p>
    </div>
    <p v-else-if="reviewError && !review" class="review-err" role="alert">
      {{ reviewError }}
    </p>
    <div
      v-else-if="review"
      class="text md-body"
      v-html="html"
    />
    <p v-else class="muted">尚无综述；请先完成检索。</p>
  </div>
</template>

<style scoped lang="scss">
.panel {
  font-size: 0.88rem;
  line-height: 1.55;
  padding: 1rem;
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: var(--radius);
}

.md-body {
  margin: 0;
  padding: 0.75rem 1rem;
  background: var(--surface-elevated);
  border: 1px solid var(--border);
  border-radius: var(--radius-sm);
  color: var(--text);
  word-break: break-word;

  :deep(h2) {
    margin: 1.1rem 0 0.45rem;
    font-size: 1.02rem;
    font-weight: 600;
    color: var(--text);
    border-bottom: 1px solid var(--border);
    padding-bottom: 0.25rem;

    &:first-child {
      margin-top: 0;
    }
  }

  :deep(h3) {
    margin: 0.85rem 0 0.35rem;
    font-size: 0.95rem;
    font-weight: 600;
  }

  :deep(p) {
    margin: 0.45rem 0;
  }

  :deep(ul),
  :deep(ol) {
    margin: 0.35rem 0 0.5rem;
    padding-left: 1.35rem;
  }

  :deep(li) {
    margin: 0.2rem 0;
  }

  :deep(strong) {
    font-weight: 600;
    color: var(--text);
  }

  :deep(blockquote) {
    margin: 0.5rem 0;
    padding: 0.35rem 0.65rem;
    border-left: 3px solid var(--accent);
    background: rgba(21, 101, 192, 0.06);
    color: var(--muted);
  }

  :deep(code) {
    font-size: 0.86em;
    background: var(--surface);
    padding: 0.1em 0.35em;
    border-radius: 3px;
    border: 1px solid var(--border);
  }
}

.muted {
  color: var(--muted);
}

.review-err {
  margin: 0;
  padding: 0.65rem 0.85rem;
  border-radius: var(--radius-sm);
  border: 1px solid var(--danger-border);
  background: var(--danger-bg);
  color: var(--danger-text);
  font-size: 0.88rem;
}

.skeleton {
  display: flex;
  flex-direction: column;
  gap: 0.55rem;
}

.sk-line {
  height: 0.65rem;
  border-radius: 4px;
  background: linear-gradient(
    90deg,
    rgba(21, 101, 192, 0.08) 0%,
    rgba(21, 101, 192, 0.18) 50%,
    rgba(21, 101, 192, 0.08) 100%
  );
  background-size: 200% 100%;
  animation: sk-shimmer 1.2s ease-in-out infinite;
}

.sk-line.short {
  width: 72%;
}

.sk-line.mid {
  width: 88%;
}

.sk-hint {
  margin: 0.35rem 0 0;
  font-size: 0.82rem;
  color: var(--muted);
}

@keyframes sk-shimmer {
  0% {
    background-position: 100% 0;
  }
  100% {
    background-position: -100% 0;
  }
}
</style>
