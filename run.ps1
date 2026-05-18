# [2026-05-18] 开发与生产启动说明（模式 B：前端控页面，API 仅 8000；生产由 Nginx 同域反代）

# ========== 开发（双进程）==========
# 终端 A
cd backend
.\.venv\Scripts\uvicorn.exe app.main:app --reload --host 127.0.0.1 --port 8000

# 终端 B
cd frontend
npm install
npm run dev
# 浏览器 http://127.0.0.1:5173 （Vite 代理 /api -> 8000）

# ========== 生产（Nginx 同域，见 deploy/README.md）==========
# 1) cd frontend && npm run build
# 2) 终端 API：cd backend && .\.venv\Scripts\uvicorn.exe app.main:app --host 127.0.0.1 --port 8000
# 3) 编辑 deploy/nginx.conf 的 root 后启动 Nginx，访问 http://localhost:8080

# ========== 无 Nginx 时本地模拟生产 ==========
# 终端 A：同上 uvicorn
# 终端 B：cd frontend && npm run build && npm run preview
# 浏览器 http://127.0.0.1:4173
