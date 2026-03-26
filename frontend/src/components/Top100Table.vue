<script setup lang="ts">
import type { ArticleItem } from '@/api/analyze';

defineProps<{
  rows: ArticleItem[];
}>();
</script>

<template>
  <div class="wrap">
    <p v-if="!rows.length" class="muted">
      近 5 年内无文献，或检索结果为空。
    </p>
    <div v-else class="table-scroll">
      <table class="table">
        <thead>
          <tr>
            <th>PMID</th>
            <th>年份</th>
            <th>IF</th>
            <th>分区</th>
            <th>期刊</th>
            <th>标题</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="(r, idx) in rows" :key="r.pmid" :class="{ stripe: idx % 2 === 1 }">
            <td class="mono">
              <a
                :href="`https://pubmed.ncbi.nlm.nih.gov/${r.pmid}/`"
                target="_blank"
                rel="noreferrer"
              >
                {{ r.pmid }}
              </a>
            </td>
            <td>{{ r.year ?? '—' }}</td>
            <td>{{ r.impact_factor?.toFixed(2) ?? '—' }}</td>
            <td>{{ r.quartile ?? '未知' }}</td>
            <td class="journal">{{ r.journal ?? '—' }}</td>
            <td class="title">{{ r.title }}</td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<style scoped lang="scss">
.wrap {
  width: 100%;
}

.muted {
  color: var(--muted);
  font-size: 0.9rem;
}

.table-scroll {
  overflow: auto;
  max-height: 420px;
  border: 1px solid var(--border);
  border-radius: var(--radius);
  background: var(--surface);
}

.table {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.82rem;

  th,
  td {
    padding: 0.45rem 0.5rem;
    text-align: left;
    border-bottom: 1px solid var(--border);
    vertical-align: top;
  }

  th {
    position: sticky;
    top: 0;
    background: #e3f2fd;
    z-index: 1;
    font-weight: 600;
    color: var(--text);
    border-bottom: 1px solid var(--border);
  }

  tbody tr.stripe td {
    background: var(--surface-elevated);
  }

  tbody tr:hover td {
    background: var(--accent-soft);
  }
}

.mono {
  font-variant-numeric: tabular-nums;
  white-space: nowrap;
}

.journal {
  max-width: 140px;
  word-break: break-word;
}

.title {
  max-width: 360px;
}
</style>
