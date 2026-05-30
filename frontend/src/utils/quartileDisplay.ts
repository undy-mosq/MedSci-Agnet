/** [2026-05-19] 分区展示：NA / 空值在界面上统一为「未知」。 */

/**
 * 功能：将后端 quartile 转为界面展示文案。
 * 输入说明：Q1–Q4、NA、null 等。
 * 输出说明：Q1–Q4 原样，其余为「未知」。
 */
export function displayQuartile(quartile: string | null | undefined): string {
  if (!quartile) {
    return '未知';
  }
  const u = quartile.trim().toUpperCase();
  if (u === 'NA' || u === 'N/A') {
    return '未知';
  }
  return quartile;
}

/**
 * 功能：统计与筛选用的分区键（与 displayQuartile 一致）。
 * 输入说明：原始 quartile。
 * 输出说明：聚合键字符串。
 */
export function quartileGroupKey(quartile: string | null | undefined): string {
  return displayQuartile(quartile);
}
