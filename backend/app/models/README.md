# models 目录说明

## 文件


| 文件            | 功能                                                                                                           |
| ------------- | ------------------------------------------------------------------------------------------------------------ |
| `__init__.py` | 包标识                                                                                                          |
| `schemas.py`  | `AnalyzeRequest`、`AnalyzeResponse`、`ArticleItem`、`CorpusStats`、`IfSummary`、`WordCloudItem`、`ReviewPayload` 等 |


## 完成情况

- 与前端 `src/api/analyze.ts` 字段对齐；`IfSummary` 使用 `min`/`max` 序列化别名。

## 修改记录

- 初版：定义 API 契约。

