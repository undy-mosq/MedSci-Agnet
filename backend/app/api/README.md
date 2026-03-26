# api 目录说明

## 文件

| 文件 | 功能 |
|------|------|
| `__init__.py` | 包标识 |
| `routes_analyze.py` | `POST /api/analyze`（PubMed、统计、词云、Top100）；`POST /api/review`（综述）；`GET /api/ping` |

## 路由与行为

| 方法 | 路径 | 说明 |
|------|------|------|
| `POST` | `/api/analyze` | 检索 PubMed，计算语料统计、近 5 年 Top100、词云。**不**调用 LLM 综述；响应中 `review` 固定为 `null`。PubMed 失败时返回 HTTP 502。 |
| `POST` | `/api/review` | 请求体为 `ReviewRequest`：客户端回传与首次分析一致的 `query`、`stats`、`articles`（仅需 `title`/`abstract` 用于综述流水线）。服务端调用 `build_review`，不重复检索 PubMed；成功返回 `ReviewPayload`（`mode` 为 `llm` 或 `template`）。 |
| `GET` | `/api/ping` | 轻量探活，返回 `{"message":"pong"}`。 |

## 完成情况

- 路由层仅做参数校验与组装；`/api/analyze` 的 HTTP 502 映射 PubMed 错误。
- 综述与检索解耦：两次 HTTP 往返，首次即可展示图表与词云。

## 修改记录

- 初版：创建分析路由与依赖注入。
- 分阶段综述：`/api/analyze` 不再生成 `review`；新增 `POST /api/review`。
