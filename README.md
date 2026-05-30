# PubMed 文献分析 Demo

基于 PubMed 检索的文献分析 Web 应用：后端 FastAPI 拉取题录并关联期刊影响因子/分区，前端 Vue 3 展示统计图表、词云、Top100 与 AI/模板综述。

## 环境要求

| 组件 | 版本建议 |
|------|----------|
| Python | 3.10+ |
| Node.js | 18+（用于前端构建与开发服务器） |
| 可选 | Nginx（生产同域部署，见 `deploy/DEPLOYMENT.md`） |

## 快速启动

### 1. 配置后端

```powershell
cd backend
copy config.ini.example config.ini
# 用编辑器填写 config.ini（至少确认路径；LLM、NCBI 密钥按需填写）
```

配置项说明见下文 [配置文件](#配置文件-configini)。

### 2. 安装并启动后端

```powershell
cd backend
py -3 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r ..\requirements.txt
.\.venv\Scripts\uvicorn.exe app.main:app --reload --host 127.0.0.1 --port 8000
```

工作目录须为 `backend`，以便正确加载 `app` 包与 `config.ini`。

### 3. 安装并启动前端（开发）

另开终端：

```powershell
cd frontend
npm install
npm run dev
```

浏览器访问 **http://127.0.0.1:5173**。前端通过 Vite 将 `/api`、`/health` 代理到 `http://127.0.0.1:8000`。

### 4. 生产 / 本地模拟生产

| 方式 | 说明 |
|------|------|
| Nginx 同域 | `npm run build` → 启动 uvicorn → 按 `deploy/DEPLOYMENT.md` 配置 Nginx，访问 `http://localhost:8080` |
| 无 Nginx | 终端 A：uvicorn；终端 B：`cd frontend && npm run build && npm run preview`，访问 **http://127.0.0.1:4173** |
| 脚本 | 仓库根目录 `run.ps1`（注释说明）、`run-prod.ps1`（preview + 需另开 API 终端） |

生产构建时 `frontend/.env.production` 中 **`VITE_API_BASE` 留空**，由 Nginx 或 Vite preview 同源反代 `/api`。

## 项目结构

```
web_demo/
├── README.md                 # 本文件：总览、启动、配置
├── requirements.txt          # Python 依赖（在 backend 虚拟环境中安装）
├── run.ps1 / run-prod.ps1    # 启动说明 / 本地 preview 脚本
├── backend/                  # FastAPI API（端口 8000）
│   ├── config.ini            # 本地配置（勿提交密钥，见 .gitignore）
│   ├── config.ini.example    # 配置模板
│   └── app/                  # 应用代码，详见 backend/BACKEND_GUIDE.md
├── frontend/                 # Vue 3 + Vite，详见 frontend/FRONTEND_GUIDE.md
│   ├── src/                  # 源码，详见 frontend/src/SOURCE_TREE.md
│   └── dist/                 # `npm run build` 产物（生产静态资源）
├── data/                     # 期刊指标 JSON，详见 data/DATA_FILES.md
│   ├── journal_metrics.json  # 主映射表（只读）
│   └── new_metrics.json      # MedSci 补全缓存（运行时可写）
└── deploy/                   # Nginx 示例，详见 deploy/DEPLOYMENT.md
```

### 各目录用途

| 目录 | 用途 |
|------|------|
| `backend/` | PubMed 检索、指标 JOIN、统计/词频/综述 API；配置 `config.ini` |
| `frontend/` | 检索界面、ECharts 图表、词云、Top100、综述 Tab |
| `data/` | 期刊影响因子与分区数据；MedSci 补全结果写入 `new_metrics.json` |
| `deploy/` | 模式 B：Nginx 托管 `frontend/dist` 并反代 `/api` 到 uvicorn |

更细的模块说明见各目录下的 `*_GUIDE.md`、`*_ROUTES.md` 等文档（原分散的 `README.md` 已改名，避免与根 README 混淆）。

## 配置文件 config.ini

路径：**`backend/config.ini`**（由 `backend/config.ini.example` 复制得到）。  
相对路径均相对于 **`backend` 目录**（与 `config.ini` 同级）。

### 配置步骤

1. `copy config.ini.example config.ini`
2. 在 `[app]` 节按需填写下列项；留空项使用代码中的默认值（见 `backend/app/config.py`）

### 主要配置项

| 键 | 说明 | 默认 / 备注 |
|----|------|-------------|
| `ncbi_api_key` | NCBI E-utilities API Key，可提高请求速率 | 可选，[NCBI 账户设置](https://www.ncbi.nlm.nih.gov/account/settings/) |
| `journal_metrics_path` | 主期刊指标 JSON | 空 → `../data/journal_metrics.json` |
| `new_journal_metrics_path` | MedSci 补全缓存 | 空 → `../data/new_metrics.json` |
| `medsci_enabled` | 是否启用 MedSci 补全 | `true` |
| `medsci_batch_size` | 单次 sync 最多刊数 | `10` |
| `medsci_min_interval_seconds` | 刊间请求间隔（秒） | `1.0` |
| `medsci_client_idle_seconds` | 无 sync/poll 超过该秒数则自动取消后台补全 | `30` |
| `llm_api_base` | OpenAI 兼容接口 Base URL | `https://api.openai.com/v1` |
| `llm_api_key` | LLM API 密钥 | 空则综述走模板，不走 LLM |
| `llm_model` | 模型名 | `gpt-4o-mini` |
| `http_timeout_seconds` | HTTP 超时 | `60` |
| `max_analyze_results` | 单次分析最大条数（后端上限） | `500` |
| `pubmed_retry_sleep_seconds` | PubMed 重试间隔 | `1.0` |

未找到 `config.ini` 时后端启动会报错并提示复制 example 文件。

### 前端环境变量（可选）

| 文件 | 变量 | 说明 |
|------|------|------|
| `frontend/.env.development` | `VITE_API_BASE` | 开发留空，走 Vite 代理 |
| `frontend/.env.production` | `VITE_API_BASE` | 生产同域留空；跨域部署时设为 API 根 URL（无末尾 `/`） |

## 核心 API（摘要）

| 方法 | 路径 | 说明 |
|------|------|------|
| `GET` | `/health` | 健康检查 |
| `POST` | `/api/analyze` | PubMed 检索 + 本地指标 JOIN |
| `POST` | `/api/metrics-enrichment/{job_id}/sync` | MedSci 批量补全 |
| `GET` | `/api/metrics-enrichment/{job_id}` | 补全进度轮询 |
| `POST` | `/api/review` | 生成综述 |
| `GET` | `/api/journal-metrics` | 主映射表 JSON |

完整路由说明见 `backend/app/api/API_ROUTES.md`。

## 文档索引

| 文档 | 内容 |
|------|------|
| `backend/BACKEND_GUIDE.md` | 后端安装、API 概览 |
| `frontend/FRONTEND_GUIDE.md` | 前端脚本、环境变量 |
| `data/DATA_FILES.md` | 指标 JSON 与补全流程 |
| `deploy/DEPLOYMENT.md` | Nginx 生产部署 |
| `backend/app/APP_PACKAGE.md` | `app` 包模块结构 |
| `backend/app/api/API_ROUTES.md` | 路由明细 |
| `backend/app/services/SERVICES.md` | 服务层说明 |
| `frontend/src/SOURCE_TREE.md` | 前端源码结构 |

## 修改记录

- [2026-05-30] 新增仓库根 `README.md`；子目录原 `README.md` 重命名为上述专用文档名。
