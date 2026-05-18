# [2026-05-18] 本地模拟生产：API + Vite preview（等同 Nginx 同域反代 /api）
# 需先：cd frontend && npm run build

Write-Host "请先在另一终端启动 API：" -ForegroundColor Yellow
Write-Host "  cd backend" -ForegroundColor Gray
Write-Host "  .\.venv\Scripts\uvicorn.exe app.main:app --host 127.0.0.1 --port 8000" -ForegroundColor Gray
Write-Host ""
Write-Host "本脚本启动 Vite preview（默认 http://127.0.0.1:4173）..." -ForegroundColor Cyan

Set-Location $PSScriptRoot\frontend
if (-not (Test-Path dist\index.html)) {
    npm run build
}
npm run preview
