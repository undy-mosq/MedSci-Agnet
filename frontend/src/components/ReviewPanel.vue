<script setup lang="ts">
import type { ReviewPayload } from '@/api/analyze';

defineProps<{
  review: ReviewPayload | null;
  reviewLoading?: boolean;
  reviewError?: string | null;
}>();
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
    <template v-else-if="review">
      <div class="badges">
        <span class="badge" :class="review.mode">
          {{ review.mode === 'llm' ? 'LLM 生成' : '模板占位' }}
        </span>
      </div>
      <pre class="text">{{ review.text }}</pre>
    </template>
    <p v-else class="muted">尚无综述；请先完成检索。</p>
  </div>
</template>

<style scoped lang="scss">
.panel {
  font-size: 0.88rem;
  line-height: 1.55;
}

.badges {
  margin-bottom: 0.65rem;
}

.badge {
  display: inline-block;
  padding: 0.2rem 0.55rem;
  border-radius: 999px;
  font-size: 0.75rem;
  font-weight: 600;

  &.template {
    background: #374151;
    color: #e5e7eb;
  }

  &.llm {
    background: rgba(61, 139, 253, 0.25);
    color: #bfdbfe;
  }
}

.text {
  margin: 0;
  white-space: pre-wrap;
  word-break: break-word;
  font-family: inherit;
  color: var(--text);
}

.muted {
  color: var(--muted);
}

.review-err {
  margin: 0;
  padding: 0.65rem 0.85rem;
  border-radius: var(--radius);
  border: 1px solid rgba(248, 113, 113, 0.45);
  background: rgba(127, 29, 29, 0.25);
  color: #fecaca;
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
    rgba(148, 163, 184, 0.15) 0%,
    rgba(148, 163, 184, 0.35) 50%,
    rgba(148, 163, 184, 0.15) 100%
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
