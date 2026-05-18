"""[2026-05-18] 纯 API 入口：移除 StaticFiles，生产由 Nginx 同域提供前端并反代 /api。"""

import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes_analyze import router as analyze_router
from app.models.schemas import HealthResponse

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
)
logger = logging.getLogger(__name__)

app = FastAPI(title="PubMed 文献分析 Demo", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(analyze_router)


@app.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    """健康检查。

    函数功能：供负载均衡或 Nginx 探活。
    输入说明：无。
    输出说明：``HealthResponse(status="ok")``。
    """
    return HealthResponse(status="ok")
