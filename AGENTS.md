# AI入境游一站式定制平台 — Agent 规则

## 项目定位
重庆入境游一站式平台，AI 驱动的行程规划 + 内容展示 + 客服系统。

## 怎么跑
```bash
# 后端（需 Python 3.8+）
cd services/planner-api && uvicorn app.main:app --port 8001

# 前端
python3 -m http.server 3000 -d frontend/public
# 或已有 Nginx 配置

# 线上
https://mmyou.top — 阿里云 ECS 47.250.175.170
```

## 技术栈
- 前端：纯 HTML/CSS/JS（`frontend/public/index.html`）
- 后端：Python FastAPI（`services/planner-api/`）
- LLM：DeepSeek-V3（OpenAI 兼容）
- 部署：Nginx + systemd（`travel-planner.service`）

## 目录约定
```
ai-travel-platform/
├── frontend/public/        ← 网站唯一源文件
├── services/planner-api/   ← 后端（FastAPI）
├── docs/                   ← 内容素材库
├── data/                   ← 数据
└── .env                    ← LLM Key（不提交）
```

## 当前状态（2026-07-20）
- 50 POI + 13景点 + 12笔记在线
- AI 行程规划 + AI客服运行中
- 待做：英文版、支付、RAG 升级
- 完整计划见 `../ai-travel-platform-dev-plan.md`
