/** [2026-05-18] 题录词频（与 backend text_mining_service 对齐，篇级去重）。 */

import type { WordCloudItem } from '@/api/analyze';

const STOP = new Set(
  `
    a an the and or but if in on at to for of as is was are were be been being
    with from by that this these those it its they them their we our you your
    he she his her has have had do does did not no nor so than then such
    can will may might should could would about into through during before
    after above below between both each few more most other some such only
    same than too very just also using use used new study patients results
    method methods data analysis based cell cells protein gene expression
    significant effect effects model models human disease treatment clinical
    one two first however there which while where when what who how all any
    both each few most other some than that these those this
  `
    .trim()
    .split(/\s+/),
);

const TOKEN_RE = /[A-Za-z][A-Za-z0-9\-]{1,48}/g;

/**
 * 功能：从单段文本提取有效词条（小写、去停用词）。
 * 输入说明：题录拼接串（标题 + 摘要）。
 * 输出说明：可迭代的词字符串。
 */
function* tokenize(text: string): Generator<string> {
  const matches = text.matchAll(TOKEN_RE);
  for (const m of matches) {
    const w = m[0].toLowerCase();
    if (STOP.has(w) || w.length < 3) continue;
    yield w;
  }
}

/**
 * 功能：统计多篇题录的篇级词频 Top N。
 * 输入说明：每篇一条文本；topN 为最多返回条数。
 * 输出说明：词云项列表，weight 为出现篇数。
 */
export function buildWordFrequencies(
  texts: string[],
  topN = 100,
): WordCloudItem[] {
  const counts = new Map<string, number>();
  for (const t of texts) {
    if (!t) continue;
    const seen = new Set<string>();
    for (const w of tokenize(t)) {
      seen.add(w);
    }
    for (const w of seen) {
      counts.set(w, (counts.get(w) ?? 0) + 1);
    }
  }
  const ranked = [...counts.entries()].sort((a, b) => b[1] - a[1]);
  return ranked.slice(0, topN).map(([word, weight]) => ({ word, weight }));
}
