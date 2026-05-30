# services 目录说明

## 文件

| 文件 | 功能 |
|------|------|
| `__init__.py` | 包标识 |
| `pubmed_service.py` | NCBI `esearch`/`efetch` |
| `pubmed_parser.py` | 解析 PubMed XML |
| `metrics_service.py` | `CompositeMetricsRepository`：主表 + `new_metrics` lookup；追加 `new_metrics` |
| `medsci_service.py` | MedSci HTML 解析：IF + 中科院大类 → Q1–Q4 |
| `metrics_enrichment.py` | 补全任务：create_job、sync 批、后台队列、poll 增量 |
| `analytics_service.py` | 统计与近 5 年 Top100 |
| `text_mining_service.py` | 词频 |
| `review_service/` | 综述 LLM / 模板 |

## 完成情况

- lookup 顺序：主表（含刊名弱匹配）→ `new_metrics`（ISSN/刊名精确）。
- MedSci 限速：`medsci_min_interval_seconds`（默认 1.0）/ 刊。
- 无客户端 sync/poll 超过 `medsci_client_idle_seconds`（默认 30s）后台自动 `cancel`。

## 修改记录

- 初版：按领域拆分。
- [2026-05-19] MedSci 补全：`medsci_service`、`metrics_enrichment`、`CompositeMetricsRepository`。
- [2026-05-19] `metrics_enrichment`：`last_client_at`、空闲自动取消。
