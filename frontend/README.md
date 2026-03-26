# frontend 目录说明

## 功能

Vue 3 + Vite + TypeScript 单页：检索 PubMed 分析结果，展示统计图表（ECharts）、词云（`wordcloud`）、Top100 表、综述。

## 完成情况

- 未使用 `vue-router` / Pinia；状态用 `ref` + `useAnalyze`。
- **界面结构**：「分析结果」单页纵向展示统计图表、词云、Top100；「综述」单独一页。主检索请求未完成时显示居中加载动画与说明。
- **检索条数**：前端固定每次分析 **100** 条（`App.vue` 中 `ANALYZE_MAX_RESULTS`），不再提供条数输入。
- **主题**：浅色医疗门户风格（顶栏蓝、正文深灰、卡片白底），与政务/医药信息类站点气质一致。
- `vite.config.ts` 将 `/api`、`/health` 代理到 `http://127.0.0.1:8000`。
- 生产构建：`npm run build` 输出 `dist/`，由 FastAPI 挂载。

## 脚本

| 命令 | 说明 |
|------|------|
| `npm install` | 安装依赖 |
| `npm run dev` | 开发服务器（默认 5173） |
| `npm run build` | 生产构建 |
| `npm run preview` | 预览构建结果 |

## 与后端字段对应

- `POST /api/analyze` 响应与 `src/api/analyze.ts` 中类型一致。
- `stats.if_summary` 中 `min`/`max` 对应后端 `IfSummary` 序列化别名。

## 双进程开发（与 backend/README 一致）

1. 后端：`uvicorn` 监听 `8000`。
2. 前端：`npm run dev`，浏览器只开 Vite 页面，API 走同源代理。

## 环境变量

- `.env.development` 中 `VITE_API_BASE` 可为空（走代理）；若前端与 API 不同源，设为 API 根 URL（无末尾斜杠）。

## 修改记录

- 初版：按计划实现组件与样式。
- 改版：双 Tab（分析结果 / 综述）、固定 100 条、浅色正式主题、统一加载态。
