# 团建活动规划 Agent

一个基于 LangGraph 的团建方案规划服务。输入人数、日期、预算与偏好后，系统从场地、餐饮、交通和活动候选项中选择组合；预算不足时会依序收缩活动、餐饮和场地，并返回可执行的方案或最低可行预算。

## 能力

- FastAPI 接口：`POST /api/team-buildings/plan`
- LangGraph 编排多类供应商选择、预算计算和自动重规划
- 默认规则引擎，支持用 LLM 为候选项排序，并在模型失败时回退规则
- Mock 供应商数据，便于本地演示与测试

## 运行

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

示例请求：

```bash
curl -X POST http://127.0.0.1:8000/api/team-buildings/plan \
  -H 'Content-Type: application/json' \
  -d '{"city":"上海","event_date":"2026-10-01","participants":30,"budget":18000,"preference":"balanced"}'
```

复制 `.env.example` 为 `.env`。保持 `PLANNER_MODE=rule` 不需要任何 API Key；启用 `llm` 时配置兼容 OpenAI 的参数。

## 测试

```bash
pytest -q
```
