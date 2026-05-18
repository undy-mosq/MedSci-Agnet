/** [2026-05-18] 仪表盘年份/分区筛选与文献过滤。 */

import { computed, ref } from 'vue';

import type { ArticleItem } from '@/api/analyze';

export interface DashboardFilterState {
  yearRange: [number, number] | null;
  quartile: string | null;
}

/** 函数功能：管理仪表盘跨图筛选状态并提供过滤方法。
 *  输入说明：无（组合式函数）。
 *  输出说明：响应式状态与 filter/clear 方法。 */
export function useDashboardFilters() {
  const yearRange = ref<[number, number] | null>(null);
  const quartile = ref<string | null>(null);

  const hasActiveFilters = computed(
    () => yearRange.value != null || quartile.value != null,
  );

  const filterLabel = computed(() => {
    const parts: string[] = [];
    if (yearRange.value) {
      parts.push(`年份 ${yearRange.value[0]}–${yearRange.value[1]}`);
    }
    if (quartile.value) {
      parts.push(`分区 ${quartile.value}`);
    }
    return parts.join(' · ');
  });

  /** 函数功能：按当前筛选条件过滤文献列表。
   *  输入说明：articles 原始列表。
   *  输出说明：过滤后的 ArticleItem[]。 */
  function filterArticles(articles: ArticleItem[]): ArticleItem[] {
    return articles.filter((a) => {
      if (quartile.value != null) {
        const q = a.quartile ?? '未知';
        if (q !== quartile.value) {
          return false;
        }
      }
      if (yearRange.value != null && a.year != null) {
        const [y0, y1] = yearRange.value;
        if (a.year < y0 || a.year > y1) {
          return false;
        }
      } else if (yearRange.value != null && a.year == null) {
        return false;
      }
      return true;
    });
  }

  function setQuartile(q: string | null) {
    quartile.value = q;
  }

  function setYearRange(range: [number, number] | null) {
    yearRange.value = range;
  }

  function clearFilters() {
    yearRange.value = null;
    quartile.value = null;
  }

  return {
    yearRange,
    quartile,
    hasActiveFilters,
    filterLabel,
    filterArticles,
    setQuartile,
    setYearRange,
    clearFilters,
  };
}
