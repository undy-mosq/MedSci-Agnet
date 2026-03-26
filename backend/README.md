# backend 目录说明

## 功能概述

FastAPI 后端：封装 NCBI E-utilities（`esearch` + `efetch`）、本地期刊指标 JOIN、统计分析、词频与综述（模板 / OpenAI 兼容 LLM）。

## 完成情况

- `GET /health` 健康检查。
- `POST /api/analyze`：检索 PubMed、返回题录+指标、统计、词云数据、近 5 年 IF Top100、综述。
- 生产环境：若存在 `frontend/dist`，启动时挂载 `StaticFiles` 提供前端单页应用。
- 配置见 `backend/config.ini`（可复制 `config.ini.example` 为 `config.ini` 后填写）。

## 安装与运行

```powershell
cd D:\13056\web_demo\backend
py -3 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\uvicorn.exe app.main:app --reload --host 127.0.0.1 --port 8000
```

默认工作目录为 `backend`（保证 `app` 包与 `config.ini` 路径正确）。`journal_metrics_path`、`frontend_dist_path` 在 ini 中为相对路径时，相对于 `backend` 目录解析；也可用绝对路径。

## 与前端联调（双进程）

1. **终端 A**：按上文启动 `uvicorn`（端口 `8000`）。
2. **终端 B**：

```powershell
cd D:\13056\web_demo\frontend
npm install
npm run dev
```

浏览器访问 Vite 开发地址（默认 `http://127.0.0.1:5173`）。请求 `/api` 由 Vite 代理到 `http://127.0.0.1:8000`。

生产构建后也可只启动后端：`npm run build` 生成 `frontend/dist` 后，访问 `http://127.0.0.1:8000/` 由 FastAPI 提供静态页与 API。

## 子目录与文件

- `app/`：应用包与 `README.md`（模块说明）。
- `config.ini` / `config.ini.example`：应用配置（密钥、LLM、路径等）。
- 仓库根 `requirements.txt`：Python 依赖。

## 修改记录

- 初版：按 PubMed 文献分析 Demo 计划实现骨架、PubMed、指标、分析、词频、综述与静态挂载。
- 配置由 `.env` 改为 `config.ini`（`app/config.py` 使用 `configparser` 读取）。
