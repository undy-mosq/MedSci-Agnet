"""API 请求/响应与领域数据结构。"""

from typing import Literal

from pydantic import BaseModel, Field


class AnalyzeRequest(BaseModel):
    """分析接口请求体。"""

    query: str = Field(..., min_length=1, description="PubMed 检索式")
    max_results: int = Field(
        default=100,
        ge=1,
        le=500,
        description="最多拉取的文献条数（服务端会再钳制）",
    )


class ArticleItem(BaseModel):
    """单条文献（对外展示）。"""

    pmid: str
    title: str
    abstract: str | None = None
    journal: str | None = None
    issn: str | None = None
    year: int | None = None
    authors: list[str] = Field(default_factory=list)
    impact_factor: float | None = None
    quartile: str | None = None


class IfSummary(BaseModel):
    """影响因子描述统计（仅统计已匹配期刊）。"""

    model_config = {"populate_by_name": True}

    mean: float | None = None
    median: float | None = None
    if_min: float | None = Field(default=None, serialization_alias="min")
    if_max: float | None = Field(default=None, serialization_alias="max")
    count_matched: int = 0


class CorpusStats(BaseModel):
    """语料与检索统计。"""

    total_hits: int = 0
    analyzed_count: int = 0
    journal_match_rate: float = 0.0
    year_distribution: dict[str, int] = Field(default_factory=dict)
    quartile_counts: dict[str, int] = Field(default_factory=dict)
    if_summary: IfSummary = Field(default_factory=IfSummary)


class WordCloudItem(BaseModel):
    """词云用词条与权重。"""

    word: str
    weight: int


class ReviewPayload(BaseModel):
    """综述结果。"""

    text: str
    mode: Literal["template", "llm"]


class ReviewRequest(BaseModel):
    """综述生成请求：由客户端回传首次分析得到的 stats 与 articles，服务端不重复检索 PubMed。"""

    query: str = Field(..., min_length=1, description="与首次分析一致的检索式")
    stats: CorpusStats = Field(..., description="语料统计（须与首次分析一致）")
    articles: list[ArticleItem] = Field(
        default_factory=list,
        description="文献列表（综述流水线仅需 title/abstract）",
    )


class AnalyzeResponse(BaseModel):
    """分析接口完整响应。"""

    articles: list[ArticleItem] = Field(default_factory=list)
    stats: CorpusStats = Field(default_factory=CorpusStats)
    top100_if_5y: list[ArticleItem] = Field(default_factory=list)
    wordcloud: list[WordCloudItem] = Field(default_factory=list)
    review: ReviewPayload | None = Field(
        default=None,
        description="首次响应为 null；综述由 POST /api/review 单独生成",
    )


class HealthResponse(BaseModel):
    """健康检查。"""

    status: str = "ok"
