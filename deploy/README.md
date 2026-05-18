# deploy 目录说明

## 文件一览

| 文件 | 功能 |
|------|------|
| `nginx.conf` | 模式 B：同域提供 `frontend/dist`，`/api/` 与 `/health` 反代到 uvicorn `127.0.0.1:8000` |

## 生产部署（Nginx 同域）

1. **构建前端**（`VITE_API_BASE` 留空，请求走相对路径 `/api`）：

```powershell
cd D:\13056\web_demo\frontend
npm run build
```

2. **启动 API**（仅 JSON，不托管静态页）：

```powershell
cd D:\13056\web_demo\backend
.\.venv\Scripts\uvicorn.exe app.main:app --host 127.0.0.1 --port 8000
```

3. **配置 Nginx**  
   - 编辑 `deploy/nginx.conf` 中 `root` 为实际 `frontend/dist` 绝对路径。  
   - 将配置 include 进 Nginx，或复制到 `conf.d/pubmed-demo.conf` 后 `nginx -t` 与 `nginx -s reload`。

4. **访问**  
   - 浏览器打开 `http://localhost:8080/`（端口以 `listen` 为准）。  
   - 页面与 `/api/*` 同源，无需 CORS；`journal-metrics.html` 的 `fetch("/api/journal-metrics")` 同样可用。

## 本地模拟生产（无 Nginx）

```powershell
# 终端 A：API
cd backend
.\.venv\Scripts\uvicorn.exe app.main:app --host 127.0.0.1 --port 8000

# 终端 B：Vite preview（带 /api 代理，与 dev 一致）
cd frontend
npm run build
npm run preview
```

浏览器访问 preview 地址（默认 `http://127.0.0.1:4173`）。

## 完成情况

- FastAPI 不再挂载 `frontend/dist`；静态资源仅由 Nginx（或 Vite preview）提供。

## 修改记录

- [2026-05-18] 新增模式 B 示例配置与部署说明。
