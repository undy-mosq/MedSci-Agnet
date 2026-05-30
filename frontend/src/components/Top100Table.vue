<!-- [2026-05-19] 分区列 NA 显示为未知。 -->
<!-- [2026-05-19] 词云高亮改为柔和底色，移除左侧竖条。 -->
<!-- [2026-05-19] 增强高亮对比度，与 hover 区分。 -->
<script setup lang="ts">
import { computed, ref } from 'vue';

import type { ArticleItem } from '@/api/analyze';
import { displayQuartile } from '@/utils/quartileDisplay';

const props = defineProps<{
  rows: ArticleItem[];
  highlightWord?: string | null;
}>();

type SortKey = 'year' | 'if' | 'quartile' | 'title';
type SortDir = 'asc' | 'desc';

const search = ref('');
const sortKey = ref<SortKey>('if');
const sortDir = ref<SortDir>('desc');
const expandedPmid = ref<string | null>(null);

/** 函数功能：切换列排序方向。
 *  输入说明：key 为排序字段。
 *  输出说明：无。 */
function toggleSort(key: SortKey) {
  if (sortKey.value === key) {
    sortDir.value = sortDir.value === 'asc' ? 'desc' : 'asc';
  } else {
    sortKey.value = key;
    sortDir.value = key === 'title' ? 'asc' : 'desc';
  }
}

/** 函数功能：判断行是否匹配高亮词。
 *  输入说明：row 为文献行。
 *  输出说明：是否匹配。 */
function rowMatchesHighlight(row: ArticleItem): boolean {
  const w = props.highlightWord?.trim().toLowerCase();
  if (!w) {
    return false;
  }
  return (
    row.title.toLowerCase().includes(w) ||
    (row.abstract?.toLowerCase().includes(w) ?? false)
  );
}

const displayRows = computed(() => {
  const q = search.value.trim().toLowerCase();
  let list = props.rows;
  if (q) {
    list = list.filter(
      (r) =>
        r.title.toLowerCase().includes(q) ||
        (r.journal?.toLowerCase().includes(q) ?? false) ||
        r.pmid.includes(q),
    );
  }
  const dir = sortDir.value === 'asc' ? 1 : -1;
  return [...list].sort((a, b) => {
    let cmp = 0;
    switch (sortKey.value) {
      case 'year':
        cmp = (a.year ?? 0) - (b.year ?? 0);
        break;
      case 'if':
        cmp = (a.impact_factor ?? -1) - (b.impact_factor ?? -1);
        break;
      case 'quartile':
        cmp = displayQuartile(a.quartile).localeCompare(displayQuartile(b.quartile));
        break;
      case 'title':
        cmp = a.title.localeCompare(b.title);
        break;
    }
    return cmp * dir;
  });
});

function sortIndicator(key: SortKey): string {
  if (sortKey.value !== key) {
    return '';
  }
  return sortDir.value === 'asc' ? ' ↑' : ' ↓';
}

function toggleExpand(pmid: string) {
  expandedPmid.value = expandedPmid.value === pmid ? null : pmid;
}

/** 函数功能：截取摘要预览。
 *  输入说明：text 摘要、max 最大长度。
 *  输出说明：截断后字符串。 */
function abstractPreview(text: string | null | undefined, max = 300): string {
  const t = text?.trim();
  if (!t) {
    return '（无摘要）';
  }
  return t.length > max ? `${t.slice(0, max)}…` : t;
}
</script>

<template>
  <div class="wrap">
    <p v-if="!rows.length" class="muted">近 5 年内无文献，或检索/筛选结果为空。</p>
    <template v-else>
      <div class="toolbar">
        <input
          v-model="search"
          class="search-input"
          type="search"
          placeholder="搜索标题、期刊或 PMID…"
          autocomplete="off"
        />
        <span class="count muted">显示 {{ displayRows.length }} / {{ rows.length }} 条</span>
      </div>
      <div class="table-scroll panel">
        <table class="table">
          <thead>
            <tr>
              <th class="sortable" @click="toggleSort('year')">年份{{ sortIndicator('year') }}</th>
              <th class="sortable" @click="toggleSort('if')">IF{{ sortIndicator('if') }}</th>
              <th class="sortable" @click="toggleSort('quartile')">
                分区{{ sortIndicator('quartile') }}
              </th>
              <th>PMID</th>
              <th>期刊</th>
              <th class="sortable" @click="toggleSort('title')">
                标题{{ sortIndicator('title') }}
              </th>
              <th class="col-expand" />
            </tr>
          </thead>
          <tbody>
            <template v-for="(r, idx) in displayRows" :key="r.pmid">
              <tr
                :class="{
                  stripe: idx % 2 === 1,
                  highlight: rowMatchesHighlight(r),
                }"
              >
                <td>{{ r.year ?? '—' }}</td>
                <td class="num">{{ r.impact_factor?.toFixed(2) ?? '—' }}</td>
                <td>{{ displayQuartile(r.quartile) }}</td>
                <td class="mono">
                  <a
                    :href="`https://pubmed.ncbi.nlm.nih.gov/${r.pmid}/`"
                    target="_blank"
                    rel="noreferrer"
                  >
                    {{ r.pmid }}
                  </a>
                </td>
                <td class="journal">{{ r.journal ?? '—' }}</td>
                <td class="title">{{ r.title }}</td>
                <td class="col-expand">
                  <button
                    type="button"
                    class="btn-expand"
                    :aria-expanded="expandedPmid === r.pmid"
                    @click="toggleExpand(r.pmid)"
                  >
                    {{ expandedPmid === r.pmid ? '收起' : '摘要' }}
                  </button>
                </td>
              </tr>
              <tr v-if="expandedPmid === r.pmid" class="abstract-row">
                <td colspan="7">
                  <p class="abstract-text">{{ abstractPreview(r.abstract) }}</p>
                </td>
              </tr>
            </template>
          </tbody>
        </table>
      </div>
    </template>
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

.toolbar {
  display: flex;
  flex-wrap: wrap;
  gap: var(--space-sm);
  align-items: center;
  margin-bottom: var(--space-sm);
}

.search-input {
  flex: 1 1 200px;
  min-width: 0;
  padding: 0.45rem 0.65rem;
  border: 1px solid var(--border);
  border-radius: var(--radius-sm);
  font-size: var(--text-sm);

  &:focus {
    outline: none;
    border-color: var(--accent);
    box-shadow: 0 0 0 2px var(--accent-soft);
  }
}

.count {
  font-size: var(--text-xs);
}

.table-scroll {
  overflow: auto;
  max-height: 480px;
}

.table {
  width: 100%;
  border-collapse: collapse;
  font-size: var(--text-sm);

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
  }

  th.sortable {
    cursor: pointer;
    user-select: none;

    &:hover {
      color: var(--accent);
    }
  }

  tbody tr.stripe td {
    background: var(--surface-elevated);
  }

  tbody tr:hover td {
    background: var(--accent-soft);
  }

  tbody tr.highlight td {
    background: var(--row-highlight-bg);
    box-shadow: inset 0 0 0 1px var(--row-highlight-border);
  }

  tbody tr.highlight .title {
    font-weight: 600;
  }
}

.mono {
  font-variant-numeric: tabular-nums;
  white-space: nowrap;
}

.num {
  font-variant-numeric: tabular-nums;
}

.journal {
  max-width: 140px;
  word-break: break-word;
}

.title {
  max-width: 360px;
}

.col-expand {
  width: 4rem;
  white-space: nowrap;
}

.btn-expand {
  padding: 0.15rem 0.45rem;
  border: 1px solid var(--border);
  border-radius: var(--radius-sm);
  background: var(--surface);
  font-size: var(--text-xs);
  cursor: pointer;
  color: var(--accent);

  &:hover {
    background: var(--accent-soft);
  }
}

.abstract-row td {
  background: var(--surface-elevated) !important;
}

.abstract-text {
  margin: 0;
  font-size: var(--text-xs);
  line-height: 1.55;
  color: var(--muted);
}
</style>
