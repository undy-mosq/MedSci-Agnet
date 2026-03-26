# components 目录说明

## 文件

| 文件 | 功能 |
|------|------|
| `SearchBar.vue` | 检索式输入、提交分析（每次固定 100 条，由 `App.vue` 传入 `runAnalyze`） |
| `StatsCharts.vue` | ECharts 年份柱状图、分区饼图、指标卡片（浅色主题配色） |
| `WordCloudView.vue` | 基于 `wordcloud` 画布词云 |
| `Top100Table.vue` | 近 5 年 IF Top100 表格与 PubMed 链接 |
| `ReviewPanel.vue` | 综述正文与模板/LLM 模式标签 |

## 完成情况

- 加载/空态/错误在 `App.vue` 与各子组件中处理；主分析阶段在 `App.vue` 展示全页加载面板。

## 修改记录

- 初版：按 Tab 拆分组件。
- 改版：`SearchBar` 取消条数输入；图表与表格配色适配浅色主题。
