"""应用配置：从 backend 目录下的 config.ini 加载。"""

from configparser import ConfigParser
from functools import lru_cache
from pathlib import Path

from pydantic import BaseModel, ConfigDict, Field


def _backend_root() -> Path:
    """backend 目录（与 `config.ini` 同级）。"""
    return Path(__file__).resolve().parents[1]


def _repo_root() -> Path:
    """仓库根目录（含 `data/`、`frontend/`）。"""
    return _backend_root().parent


def _default_metrics_path() -> Path:
    """默认期刊指标文件路径。"""
    return _repo_root() / "data" / "journal_metrics.json"


def _default_dist_path() -> Path:
    """默认前端构建产物目录。"""
    return _repo_root() / "frontend" / "dist"


def _config_ini_path() -> Path:
    return _backend_root() / "config.ini"


def _resolve_path(raw: str | None, default: Path) -> Path:
    """将配置中的路径转为绝对路径；相对路径相对于 `backend` 目录。"""
    if raw is None or not str(raw).strip():
        return default
    p = Path(raw.strip())
    if p.is_absolute():
        return p
    return (_backend_root() / p).resolve()


def _load_ini_dict(path: Path) -> dict[str, str | float | int | Path | None]:
    """从 config.ini 解析为扁平字典。"""
    if not path.is_file():
        raise FileNotFoundError(
            f"未找到配置文件: {path}。请将 config.ini.example 复制为 config.ini 并填写。"
        )
    cp = ConfigParser(interpolation=None)
    cp.read(path, encoding="utf-8")
    section = "app"
    if not cp.has_section(section):
        raise ValueError(f"配置文件缺少 [{section}] 节: {path}")

    def opt_str(key: str) -> str | None:
        if not cp.has_option(section, key):
            return None
        v = cp.get(section, key, fallback="").strip()
        return v if v else None

    def str_default(key: str, default: str) -> str:
        v = opt_str(key)
        return v if v is not None else default

    def float_default(key: str, default: float) -> float:
        if not cp.has_option(section, key):
            return default
        raw = cp.get(section, key, fallback="").strip()
        if not raw:
            return default
        return float(raw)

    def int_default(key: str, default: int) -> int:
        if not cp.has_option(section, key):
            return default
        raw = cp.get(section, key, fallback="").strip()
        if not raw:
            return default
        return int(raw)

    ncbi = opt_str("ncbi_api_key")
    jm_raw = opt_str("journal_metrics_path")
    fd_raw = opt_str("frontend_dist_path")

    return {
        "ncbi_api_key": ncbi,
        "journal_metrics_path": _resolve_path(jm_raw, _default_metrics_path()),
        "llm_api_base": str_default(
            "llm_api_base",
            "https://api.openai.com/v1",
        ),
        "llm_api_key": opt_str("llm_api_key"),
        "llm_model": str_default("llm_model", "gpt-4o-mini"),
        "frontend_dist_path": _resolve_path(fd_raw, _default_dist_path()),
        "http_timeout_seconds": float_default("http_timeout_seconds", 60.0),
        "max_analyze_results": int_default("max_analyze_results", 500),
        "pubmed_retry_sleep_seconds": float_default(
            "pubmed_retry_sleep_seconds",
            1.0,
        ),
    }


class Settings(BaseModel):
    """全局配置。"""

    model_config = ConfigDict(extra="ignore")

    ncbi_api_key: str | None = None
    journal_metrics_path: Path = Field(default_factory=_default_metrics_path)
    llm_api_base: str = "https://api.openai.com/v1"
    llm_api_key: str | None = None
    llm_model: str = "gpt-4o-mini"
    frontend_dist_path: Path = Field(default_factory=_default_dist_path)
    http_timeout_seconds: float = 60.0
    max_analyze_results: int = 500
    pubmed_retry_sleep_seconds: float = 1.0


@lru_cache
def get_settings() -> Settings:
    """返回单例配置（测试时可 `get_settings.cache_clear()`）。"""
    data = _load_ini_dict(_config_ini_path())
    return Settings.model_validate(data)

