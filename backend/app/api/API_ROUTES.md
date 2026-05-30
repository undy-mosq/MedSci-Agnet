# api 目录说明

## 文件

| 文件 | 功能 |
|------|------|
| `__init__.py` | 包标识 |
| `routes_analyze.py` | `POST /api/analyze`；MedSci 补全 `sync` / `poll` / `cancel`；`POST /api/review`；`GET /api/journal-metrics`；`GET /api/ping` |

## 路由与行为

| 方法 | 路径 | 说明 |
|------|------|------|
| `POST` | `/api/analyze` | PubMed + **本地** `journal_metrics` + `new_metrics` JOIN；返回 `articles`、`total_hits`、`enrichment`（`job_id`、`pending_count`、`needs_enrichment`）。**不**请求 MedSci。 |
| `POST` | `/api/metrics-enrichment/{job_id}/sync` | 同步批 MedSci 补全（默认最多 10 本，`?limit=` 可选）；返回本批 `new_entries`；若有剩余则启动后台。503：`medsci_enabled=false`。 |
| `GET` | `/api/metrics-enrichment/{job_id}` | 轮询增量；`?since_seq=` 只返回新条目。404：任务不存在。 |
| `POST` | `/api/metrics-enrichment/{job_id}/cancel` | 取消后台补全；关页或新检索时客户端应调用。 |
| `POST` | `/api/review` | 客户端回传 `query`、`stats`、`articles` 生成综述；不重复 PubMed。 |
| `GET` | `/api/journal-metrics` | 仅主表 `journal_metrics_path` JSON。 |
| `GET` | `/api/ping` | `{"message":"pong"}` |

### `POST /api/analyze` 响应 `enrichment`

| 字段 | 说明 |
|------|------|
| `job_id` | 补全任务 UUID；无待补全或未启用 MedSci 时为 `null` |
| `pending_count` | 待 MedSci 的去重刊数 |
| `needs_enrichment` | 是否应调用 `sync` |

### `POST .../sync` 响应要点

`sync_enriched_count`、`pending_count`、`failed_count`、`seq`、`new_entries`（本批）、`background_started`、`status`（`running` \| `completed`）。

### `GET ...` 轮询响应要点

`new_entries`（`seq > since_seq`）、`status`、`pending_count`、`seq`。

## 完成情况

- 首轮 analyze 与 MedSci 解耦，缩短首包时间。
- 补全写入 `data/new_metrics.json`，主表只读。

## 修改记录

- 初版：分析路由与依赖注入。
- 分阶段综述：`POST /api/review`。
- [2026-05-18] `/api/analyze` 瘦身。
- [2026-05-19] MedSci 分层补全 API；analyze 返回 `enrichment`。
- [2026-05-19] 补全：`medsci_client_idle_seconds` 无 sync/poll 超时自动取消；客户端 cancel + keepalive。
