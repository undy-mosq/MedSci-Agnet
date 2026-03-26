# app 包说明

## 模块结构

| 路径 | 功能 |
|------|------|
| `main.py` | FastAPI 实例、CORS、`/health`、注册 `api` 路由、启动时挂载 `frontend/dist` |
| `config.py` | `config.ini` + Pydantic：NCBI 密钥、期刊路径、LLM、超时、最大条数 |
| `models/schemas.py` | 请求/响应 Pydantic 模型 |
| `api/routes_analyze.py` | `POST /api/analyze`、`GET /api/ping` |
| `services/pubmed_service.py` | `esearch` + `efetch` 编排 |
| `services/pubmed_parser.py` | efetch XML → 字典列表 |
| `services/metrics_service.py` | 加载 `journal_metrics.json`、ISSN/刊名 lookup |
| `services/analytics_service.py` | 年分布、分区、IF 统计、近 5 年 Top100 |
| `services/text_mining_service.py` | 英文词频（停用词） |
| `services/review_service/` | 无密钥模板综述 + LangChain LCEL 多段 OpenAI 兼容调用 |

子目录 `api/`、`models/`、`services/` 另有各自 `README.md`。

## 完成情况

- 依赖方向：`routes` → `services` / `schemas`，`pubmed_service` → `parser`，无循环引用。

## 修改记录

- 初版：按计划拆分服务与路由。
- 配置加载由 `.env` / `pydantic-settings` 改为 `backend/config.ini`。
