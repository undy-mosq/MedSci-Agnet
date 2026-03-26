# data 目录说明

## 文件一览

| 文件 | 功能 |
|------|------|
| `journal_metrics.json` | 本地期刊指标：规范化刊名 → 影响因子、JCR 分区（Q1–Q4 或 NA）。可选字段 `issn` 用于与 PubMed 条目的 ISSN 对齐；当前数据集以刊名为主、可无 ISSN。PubMed 不返回 IF/Q，分析结果中的 IF/Q 均来自此表。 |

## 完成情况

- 已扩充为大规模刊名列表（数千条），字段 `journal_name`、`impact_factor`、`quartile`；与 `backend/app/services/metrics_service.py` 的加载逻辑一致。
- 未命中期刊在界面显示为「未知」，分区统计中单列为「未知」。

## 修改记录

- 初版：JSON 数组，字段 `issn`、`journal_name`、`impact_factor`、`quartile`。
- 现行版：以刊名表为主，可不含 `issn`；后端仍支持带 `issn` 的条目以便 ISSN 优先匹配。

## 数据来源与范围

- Demo 数据可为公开整理的期刊列表片段或手工录入；**不保证覆盖全部 PubMed 期刊**。
- 答辩时需说明：指标为本地对齐表，非 NCBI 官方字段。
