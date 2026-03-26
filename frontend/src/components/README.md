# components 目录说明

## 文件

| 文件 | 功能 |
|------|------|
| `SearchBar.vue` | 关键词、条数上限、提交检索 |
| `StatsCharts.vue` | ECharts 年份柱状图、分区饼图、指标卡片 |
| `WordCloudView.vue` | 基于 `wordcloud` 画布词云 |
| `Top100Table.vue` | 近 5 年 IF Top100 表格与 PubMed 链接 |
| `ReviewPanel.vue` | 综述正文与模板/LLM 模式标签 |

## 完成情况

- 加载/空态/错误在 `App.vue` 与各子组件中处理。

## 修改记录

- 初版：按 Tab 拆分组件。
