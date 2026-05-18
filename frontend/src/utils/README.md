# utils 目录说明

## 文件

| 文件 | 功能 |
|------|------|
| `corpusStats.ts` | 与后端语料统计 / Top100 对齐的前端合并与计算（分批分析等场景） |
| `chartPalette.ts` | 词云与「分区分布」饼图共用配色；`wordcloudColor`、`quartileSectorColor`、`quartileKeysForStack`（年份堆积柱系列顺序） |

## 完成情况

- 配色与 `StatsCharts.vue`、`WordCloudView.vue` 联动，修改色板时优先改 `chartPalette.ts`。

## 修改记录

- 新增 `chartPalette.ts`，统一词云与分区图颜色风格。
