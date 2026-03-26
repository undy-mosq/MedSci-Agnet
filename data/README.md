# data 目录说明

## 文件一览

| 文件 | 功能 |
|------|------|
| `journal_metrics.json` | 本地期刊指标：ISSN、规范化刊名 → 影响因子、JCR 分区（Q1–Q4 或 NA）。PubMed 不返回 IF/Q，分析结果中的 IF/Q 均来自此表。 |

## 完成情况

- 已提供示例条目（Nature、Science、Cell 等），用于演示匹配与 Top100 排序。
- 未命中期刊在界面显示为「未知」，分区统计中单列为「未知」。

## 修改记录

- 初版：按计划建立 JSON 数组结构，字段 `issn`、`journal_name`、`impact_factor`、`quartile`。

## 数据来源与范围

- Demo 数据可为公开整理的期刊列表片段或手工录入；**不保证覆盖全部 PubMed 期刊**。
- 答辩时需说明：指标为本地对齐表，非 NCBI 官方字段。
