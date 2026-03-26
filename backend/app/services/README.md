# services 目录说明

## 文件

| 文件 | 功能 |
|------|------|
| `__init__.py` | 包标识 |
| `pubmed_service.py` | NCBI `esearch`/`efetch`，批量 ID，礼貌延迟 |
| `pubmed_parser.py` | 解析 PubMed XML，无网络依赖 |
| `metrics_service.py` | `JournalMetricsRepository`：单例加载 JSON、lookup |
| `analytics_service.py` | 统计与近 5 年 Top100（按 IF 降序） |
| `text_mining_service.py` | 词频 Top N |
| `review_service/` | 模板综述与 LangChain LCEL 多段 LLM（Map→可选 Reduce→Final）；见包内 `README.md` |

## 完成情况

- 单测可单独 `import` 各模块；`pubmed_parser.parse_efetch_xml` 可固定 XML 片段断言。

## 修改记录

- 初版：按领域拆分实现。
