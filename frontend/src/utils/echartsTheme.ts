/** [2026-05-18] ECharts 与全局 CSS 变量对齐的基础主题。 */

export const CHART_COLORS = {
  text: '#37474f',
  muted: '#78909c',
  axis: '#b0bec5',
  split: '#eceff1',
  tooltipBg: '#ffffff',
} as const;

/** 函数功能：合并 ECharts 基础配置（背景、文字、tooltip 样式）。
 *  输入说明：partial 为需覆盖的片段。
 *  输出说明：完整 option 片段对象。 */
export function echartsBase(partial: Record<string, unknown> = {}) {
  return {
    backgroundColor: 'transparent',
    textStyle: { color: CHART_COLORS.text },
    tooltip: {
      backgroundColor: CHART_COLORS.tooltipBg,
      borderColor: CHART_COLORS.axis,
      textStyle: { color: CHART_COLORS.text },
    },
    ...partial,
  };
}

/** 函数功能：标准直角坐标 grid 边距。
 *  输入说明：bottom 为图例/缩放条预留高度。
 *  输出说明：grid 配置对象。 */
export function chartGrid(bottom = 44) {
  return { left: 48, right: 16, top: 32, bottom };
}

/** 函数功能：类目轴默认样式。
 *  输入说明：rotate 为标签旋转角度。
 *  输出说明：xAxis 片段。 */
export function categoryAxis(rotate = 0) {
  return {
    type: 'category' as const,
    axisLine: { lineStyle: { color: CHART_COLORS.axis } },
    axisLabel: { color: CHART_COLORS.muted, rotate },
  };
}

/** 函数功能：数值轴默认样式。
 *  输入说明：name 为轴名称。
 *  输出说明：yAxis 片段。 */
export function valueAxis(name = '篇数') {
  return {
    type: 'value' as const,
    name,
    nameTextStyle: { color: CHART_COLORS.muted },
    axisLine: { show: true, lineStyle: { color: CHART_COLORS.axis } },
    axisLabel: { color: CHART_COLORS.muted },
    splitLine: { lineStyle: { color: CHART_COLORS.split } },
  };
}

/** 函数功能：横向条形图期刊名过长时的 y 轴缩放。
 *  输入说明：count 为期刊条数。
 *  输出说明：dataZoom 数组。 */
export function dataZoomForJournals(count: number) {
  if (count <= 12) {
    return [];
  }
  const end = Math.min(100, Math.round((12 / count) * 100));
  return [
    { type: 'inside' as const, yAxisIndex: 0, start: 100 - end, end: 100 },
    { type: 'slider' as const, yAxisIndex: 0, width: 14, right: 4, start: 100 - end, end: 100 },
  ];
}
