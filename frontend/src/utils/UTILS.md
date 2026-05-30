# utils 目录说明

## 文件

| 文件 | 功能 |
|------|------|
| `corpusStats.ts` | 语料统计与近 5 年 IF Top100（`useAnalyze` 主流程） |
| `wordFreq.ts` | 题录篇级词频 Top N，供词云（与后端 `text_mining_service` 对齐） |
| `chartPalette.ts` | 词云与「分区分布」饼图共用配色；`wordcloudColor`、`quartileSectorColor`、`quartileKeysForStack`（年份堆积柱系列顺序） |
| `patchArticleMetrics.ts` | MedSci 补全 `new_entries` 合并到 `articles`（ISSN 优先） |
| `quartileDisplay.ts` | 界面展示分区：`NA`/空 →「未知」；统计与筛选用 `quartileGroupKey` |
| `articleAggregates.ts` | 期刊 Top、IF 数值轴直方图（含空桶与域边界）、摘要覆盖率；`journalDetailForName` 供期刊图点击详情 |

## 完成情况

- 配色与 `StatsCharts.vue`、`WordCloudView.vue` 联动；统计/词云在 analyze 响应后由 `useAnalyze` 调用本目录工具。

## 修改记录

- 新增 `chartPalette.ts`，统一词云与分区图颜色风格。
- [2026-05-18] 新增 `wordFreq.ts`；`corpusStats` 接入主分析流程。
- [2026-05-19] 新增 `quartileDisplay.ts`；饼图/表格 NA 并入「未知」。
- [2026-05-19] `articleAggregates` 新增 `journalDetailForName`。
- [2026-05-19] `ifHistogram` 返回 `IfHistogramResult`（保留空桶、step/域边界）。
