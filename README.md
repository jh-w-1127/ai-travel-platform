# AI Travel Platform — Chongqing MVP

> 一站式入境游定制平台 | 重庆打样 | 已上线 https://mmyou.top

## Quick Start

### 1. Start Backend
```bash
cd services/planner-api
cp .env.example .env     # 配置 LLM_API_KEY
pip install -r requirements.txt
python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8001
```

### 2. Start Frontend
```bash
cd frontend/public
python3 -m http.server 3000
# 或直接用 Nginx 指向此目录
```

### 3. Open
- Live: https://mmyou.top
- Local: http://localhost:3000
- API Docs: http://localhost:8001/docs
- Health: http://localhost:8001/api/health

## 当前内容

- 📍 **13 个景点故事** — 武隆/洪崖洞/大足石刻/磁器口/长江索道/白帝城/巫山小三峡等
- 📝 **12 篇旅行笔记** — 电影彩蛋/本地人私藏/打卡故事/户外体验
- 🧭 **AI 行程定制** — DeepSeek Function Calling 智能编排 + 预算报价
- 🤖 **AI 旅行助手** — 关键词+LLM 双模式，支持转人工

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | /api/health | Health check |
| GET | /api/planner/pois | List/search POIs |
| GET | /api/planner/pois/:id | POI detail |
| GET | /api/planner/itinerary/generate | Quick generate itinerary (template) |
| POST | /api/planner/itinerary/ai-plan | AI-powered itinerary (SSE streaming) |
| POST | /api/planner/chat | SSE dialog chat |
| GET | /api/planner/price-estimate | Price estimate |
| POST | /api/ai/ask | AI客服问答 |
| POST | /api/ai/handoff | 转人工客服 |
| GET | /api/ai/handoffs | 查看转人工列表 |

## 技术栈

| 层级 | 技术 |
|------|------|
| 前端 | 纯 HTML/CSS/JS（Nginx 托管） |
| 后端 | Python FastAPI |
| LLM | DeepSeek-V3（OpenAI 兼容 API） |
| 数据 | 内存存储（50 POI，5 品类） |
| 部署 | 阿里云 ECS + Nginx + systemd |

## 开发计划

详见 [开发计划](../ai-travel-platform-dev-plan.md)
