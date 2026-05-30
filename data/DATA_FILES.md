# data 目录说明

> 配置与启动见根目录 `README.md`。

## 文件一览

| 文件 | 功能 |
|------|------|
| `journal_metrics.json` | **主映射表**（只读）：刊名 / ISSN → 影响因子、分区（Q1–Q4 或 NA）。PubMed 不返回 IF/分区，首轮分析仅查此表与 `new_metrics.json`。 |
| `new_metrics.json` | **MedSci 补全缓存**（运行时可追加）：未命中主表时由后端抓取 MedSci 中科院大类 + IF 后写入；**不**合并进 `journal_metrics.json`。 |

## 补全流程（与 API 对应）

1. `POST /api/analyze`：PubMed + 本地两表 lookup，**不访问 MedSci**；返回 `enrichment.job_id`（若有未知刊）。
2. `POST /api/metrics-enrichment/{job_id}/sync`：同步最多 10 本（默认），≥1 秒/刊；写入 `new_metrics.json`。
3. `GET /api/metrics-enrichment/{job_id}?since_seq=`：轮询后台增量。
4. 下次分析同一刊将直接命中 `new_metrics.json`。

## 完成情况

- 主表：数千条 `journal_name`、`impact_factor`、`quartile`；与 `metrics_service.CompositeMetricsRepository` 一致。
- 补全表：MedSci 来源字段含 `source`、`cas_bigclass`、`fetched_at`。
- 未命中且未补全成功：界面显示「未知」。

## 修改记录

- 初版：仅 `journal_metrics.json`。
- [2026-05-19] 新增 `new_metrics.json` 与 MedSci 分层补全；分区口径说明为中科院大类（界面仍用 Q1–Q4 表示 1–4 区）。

## 数据来源与范围

- 主表：公开整理或手工录入，不保证覆盖全部 PubMed 期刊。
- 补全：MedSci 页面解析（非官方 API），课程 Demo 用途，需限速与合规说明。
