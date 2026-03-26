# api 目录说明

## 文件

| 文件 | 功能 |
|------|------|
| `__init__.py` | 包标识 |
| `routes_analyze.py` | `POST /api/analyze` 聚合各服务；`GET /api/ping` |

## 完成情况

- 路由层仅做参数校验与组装，HTTP 502 映射 PubMed 错误。

## 修改记录

- 初版：创建分析路由与依赖注入。
