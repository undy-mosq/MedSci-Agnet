# src 目录说明

## 结构

| 路径 | 功能 |
|------|------|
| `main.ts` | 创建应用、注册 `vue-echarts`、全局样式 |
| `App.vue` | 顶栏搜索、Tab、加载/错误/空态 |
| `api/analyze.ts` | `fetch` 封装 `POST /api/analyze` 与类型 |
| `composables/useAnalyze.ts` | `loading` / `error` / `result` / `runAnalyze` |
| `components/` | 见 `components/README.md` |
| `styles/main.scss` | 全局变量与布局 |
| `types/wordcloud.d.ts` | `wordcloud` 模块声明 |
| `vite-env.d.ts` | Vite 环境类型 |

## 完成情况

- 与计划一致：最简单页 + Tab 切换四类视图。

## 修改记录

- 初版：建立目录与类型。
