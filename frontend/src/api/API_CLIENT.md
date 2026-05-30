# `src/api` 目录说明

## 文件

| 文件 | 功能 |
|------|------|
| `client.ts` | `apiBase` / `apiUrl`；生产 Nginx 同域时 `VITE_API_BASE` 留空 |
| `analyze.ts` | `POST /api/analyze`；MedSci `sync` / `poll` / `cancel` / `cancelKeepalive`；`AnalyzeResult` 在 composable 合并 |
| `review.ts` | `POST /api/review`：基于首次返回的 `stats` 与 `articles` 生成综述（LLM / 模板） |

## 完成情况

- 分析接口与综述接口分两次 HTTP 往返；统计与词云在 `useAnalyze` 内本地计算后展示，综述异步加载。

## 修改记录

- 新增 `review.ts` 与本文档；`AnalyzeApiResponse.review` 可为 `null`，由 `useAnalyze` 调用 `postReview` 合并。
- [2026-05-18] 新增 `client.ts`；`AnalyzeApiResponse` / `AnalyzeResult` 拆分。
- [2026-05-18] `/api/analyze` 不再返回 stats/wordcloud/top100，改由前端 `corpusStats` + `wordFreq` 计算。
- [2026-05-19] `postMetricsEnrichmentCancelKeepalive`；`useAnalyze` 新检索/关页取消补全。
