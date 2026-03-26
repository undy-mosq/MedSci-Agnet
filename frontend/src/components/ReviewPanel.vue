<script setup lang="ts">
import type { ReviewPayload } from '@/api/analyze';

defineProps<{
  review: ReviewPayload | null;
}>();
</script>

<template>
  <div class="panel">
    <template v-if="review">
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
</style>
