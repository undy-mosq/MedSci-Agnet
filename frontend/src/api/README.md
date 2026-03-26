# `src/api` 目录说明

## 文件

| 文件 | 功能 |
|------|------|
| `analyze.ts` | `POST /api/analyze`：PubMed 检索、统计、词云、Top100；`review` 字段首次为 `null` |
| `review.ts` | `POST /api/review`：基于首次返回的 `stats` 与 `articles` 生成综述（LLM / 模板） |

## 完成情况

- 分析接口与综述接口分两次 HTTP 往返，首屏可先看统计与词云，综述异步加载。

## 修改记录

- 新增 `review.ts` 与本文档；`AnalyzeResponse.review` 可为 `null`，由 `useAnalyze` 在首轮成功后调用 `postReview` 合并结果。
