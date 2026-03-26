# review_service 包说明

## 文件

| 文件 | 功能 |
|------|------|
| `__init__.py` | 对外导出 `build_review`、`generate_llm_review`（保持 `app.services.review_service` 导入路径） |
| `template.py` | 无 LLM 密钥时的结构化中文模板综述 |
| `batching.py` | `tiktoken` 按模型编码估算 token；题录格式化；Map 分批；中间摘要过长时的分块；Final 输入预算判断 |
| `llm_chains.py` | `ChatOpenAI`；Map / Reduce / Final / **Direct**（题录总字符 &lt; 5000 时单次生成）的 LCEL 链；终稿为中文 Markdown（先总说要点数，再 `##` 分述） |
| `pipeline.py` | `generate_llm_review`：题录拼接长度 &lt; 5000 字符则只跑 Direct；否则 Map → 可选 Reduce → Final；异常时返回 `None`；`build_review` 回退模板 |

## 完成情况

- 已用 **LCEL** 实现 **无记忆** 的多段调用；状态仅在单次请求内传递。
- Map 每批输出英文要点 + `Themes:` 行；Final / Direct 输出中文 Markdown 综述（总述 + `##` 分述）。
- 题录全文（Title+Abstract 拼接）总字符数 **&lt; 5000** 时跳过 Map/Reduce，仅用 Direct 一次调用。
- 中间摘要超过 Final 预算时，按 token 分块调用 Reduce 链压缩，直至满足预算或超过最大轮次（此时整次失败并回退模板）。

## 与旧版差异（原单文件 `review_service.py`）

| 项目 | 旧版 | 当前 |
|------|------|------|
| LLM 调用 | 单次 `httpx` 拼接全部摘要 | **分批 Map** + 可选 **Reduce** + **Final**，避免超长 prompt |
| 依赖 | 仅 `httpx` | `langchain-core`、`langchain-openai`、`tiktoken` |
| 对外 API | `build_review`、`generate_llm_review` | **不变** |

## 修改记录

- 按分层综述计划拆包：模板 / 分批 / 链 / 流水线。
