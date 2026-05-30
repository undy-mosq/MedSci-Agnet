# models 目录说明

## 文件


| 文件            | 功能                                                                                                           |
| ------------- | ------------------------------------------------------------------------------------------------------------ |
| `__init__.py` | 包标识                                                                                                          |
| `schemas.py`  | `AnalyzeRequest`、`AnalyzeResponse`、`ArticleItem`、`CorpusStats`、`IfSummary`、`WordCloudItem`、`ReviewPayload` 等 |


## 完成情况

- 与前端 `src/api/analyze.ts` 对齐；`AnalyzeResponse` 仅含 `articles`、`total_hits`、`review`；`CorpusStats` 等供 `/api/review` 使用。

## 修改记录

- 初版：定义 API 契约。
- [2026-05-18] `AnalyzeResponse` 移除 stats、wordcloud、top100_if_5y。

