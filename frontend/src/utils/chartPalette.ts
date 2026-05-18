/**
 * 图表与词云共用：以蓝 / 青绿 / 靛蓝 / 蓝灰为主色，饱和度与明度拉开，避免糊成一片，
 * 整体仍保持医疗信息类界面常见的冷色专业风格。
 */

/** 词云用色（条数多，覆盖色相带） */
export const PALETTE_WORDCLOUD = [
  '#0d47a1',
  '#1565c0',
  '#0277bd',
  '#01579b',
  '#00838f',
  '#00695c',
  '#00897b',
  '#283593',
  '#303f9f',
  '#3949ab',
  '#455a64',
  '#546e7a',
  '#006064',
] as const;

/** 稳定哈希：同一词每次渲染颜色一致，相邻词也易错开 */
export function colorIndexForWord(label: string): number {
  let h = 2166136261;
  for (let i = 0; i < label.length; i++) {
    h ^= label.charCodeAt(i);
    h = Math.imul(h, 16777619);
  }
  return Math.abs(h) % PALETTE_WORDCLOUD.length;
}

export function wordcloudColor(word: string): string {
  return PALETTE_WORDCLOUD[colorIndexForWord(word)] ?? '#1565c0';
}

/**
 * 分区饼图：扇区少，用固定映射，色相与词云同一色系内但彼此区分明显。
 * Q1–Q4 用蓝 / 青绿 / 靛蓝 / 蓝灰；未知与 NA 用中性灰阶。
 */
export function quartileSectorColor(name: string): string {
  const u = name.trim().toUpperCase();
  if (u === 'Q1') return '#0d47a1';
  if (u === 'Q2') return '#00897b';
  if (u === 'Q3') return '#283593';
  if (u === 'Q4') return '#455a64';
  if (u === 'NA' || u === 'N/A') return '#78909c';
  if (name === '未知') return '#b0bec5';
  return '#546e7a';
}

/** 堆积柱系列顺序（自下而上与图例一致） */
const QUARTILE_STACK_ORDER: string[] = ['Q1', 'Q2', 'Q3', 'Q4', 'NA', 'N/A', '未知'];

/** 将数据中出现的分区名排序为堆积柱用的稳定顺序 */
export function quartileKeysForStack(allKeys: Iterable<string>): string[] {
  const set = new Set(allKeys);
  const fixed = QUARTILE_STACK_ORDER.filter((k) => set.has(k));
  const rest = [...set]
    .filter((k) => !QUARTILE_STACK_ORDER.includes(k))
    .sort((a, b) => a.localeCompare(b));
  return [...fixed, ...rest];
}
