# components 目录说明

## 文件

| 文件 | 功能 |
|------|------|
| `SearchBar.vue` | 检索式输入；使用说明 `<details>` 折叠；提交分析（500 条） |
| `YearRangeBar.vue` | 图表区顶部单轨道双拇指年份拉条，驱动全局年份筛选 |
| `StatsCharts.vue` | 指标卡、IF 摘要、年份/分区/期刊/IF 图；饼图分区筛选 |
| `WordCloudView.vue` | 词云 + Top20；受控 `selected-word`；词频指纹跳过重绘；MedSci 补全不闪 |
| `Top100Table.vue` | 近 5 年 Top100：排序、搜索、摘要展开、词云匹配行高亮（`row-highlight-*`） |
| `ReviewPanel.vue` | 综述 Markdown 渲染（`marked`） |

## 完成情况

- 年份筛选由 `YearRangeBar` 统一提供，位于 IF 摘要与图表网格之间；年份分布图 X 轴随拉条裁剪，柱高为全库计数。
- 加载/空态/错误在 `App.vue` 与各子组件中处理。

## 修改记录

- 初版：按 Tab 拆分组件。
- [2026-05-18] 前端显示优化：panel 样式、新图表、表格与词云交互。
- [2026-05-18] 年份公共拉条上移：`YearRangeBar.vue`。
- [2026-05-19] 年份分布图 X 轴与 `yearRange` 联动：`StatsCharts.vue`。
- [2026-05-19] 词云 toggle 取消 Top100 高亮；图表 2×2 网格；期刊 Top12 点击详情。
- [2026-05-19] 高亮增强；`App` 仅 `onSearch` 清筛选/高亮；词云指纹重绘；期刊选中 MedSci 补全保留。
