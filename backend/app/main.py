"""FastAPI 应用入口：CORS、API 路由、生产环境静态资源。"""

import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.api.routes_analyze import router as analyze_router
from app.config import get_settings
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
    """健康检查。"""
    return HealthResponse(status="ok")


@app.on_event("startup")
def startup_mount_static() -> None:
    """若存在 frontend/dist 则挂载为静态站点（生产联调）。"""
    settings = get_settings()
    dist = settings.frontend_dist_path
    if not dist.is_dir():
        logger.info("未挂载静态资源（目录不存在）: %s", dist)
        return
    index = dist / "index.html"
    if not index.is_file():
        logger.warning("dist 中缺少 index.html: %s", index)
        return
    app.mount(
        "/",
        StaticFiles(directory=str(dist), html=True),
        name="frontend",
    )
    logger.info("已挂载前端静态目录: %s", dist)
