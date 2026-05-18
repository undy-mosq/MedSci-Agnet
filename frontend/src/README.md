# src 目录说明

## 结构

| 路径 | 功能 |
|------|------|
| `main.ts` | 创建应用、注册 `vue-echarts`（含 DataZoom）、全局样式 |
| `App.vue` | 顶栏、检索、Tab、筛选条、仪表盘组合 |
| `api/` | `fetch` 封装，见 `api/README.md` |
| `composables/useAnalyze.ts` | 分析/综述请求状态 |
| `composables/useDashboardFilters.ts` | 年份区间、分区筛选与文献过滤 |
| `components/` | 见 `components/README.md` |
| `utils/articleAggregates.ts` | 期刊 Top、IF 直方图、摘要覆盖率（前端聚合） |
| `utils/echartsTheme.ts` | ECharts 基础主题与 dataZoom 辅助 |
| `utils/chartPalette.ts` | 分区/词云配色 |
| `utils/corpusStats.ts` | 与后端对齐的语料统计（分批合并用） |
| `styles/main.scss` | 设计令牌、panel、筛选条、section 标题 |
| `types/wordcloud.d.ts` | `wordcloud` 模块声明 |
| `vite-env.d.ts` | Vite 环境类型 |

## 完成情况

- 仪表盘：指标卡、年份/分区/期刊/IF 图表、词云、Top100 表、综述 Tab。
- 交互：分区饼图点击、顶部 `YearRangeBar` 年份筛选、筛选条清除、词云/词条表点击高亮 Top100。
- Top100：排序、搜索、摘要展开。

## 修改记录

- 初版：建立目录与类型。
- [2026-05-18] 前端显示优化：设计令牌、筛选 composable、articles 本地聚合图表。
- [2026-05-18] 年份筛选改为图表区顶部公共拉条 `YearRangeBar`。
