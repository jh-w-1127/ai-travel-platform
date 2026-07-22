# 技术架构

## 架构模式

纯 HTML 前端 + FastAPI 后端 + Nginx 反向代理，无框架前端以降低复杂度。

## 系统架构图

```
用户浏览器 (mmyou.top)
       │
       ▼
Nginx (:80) ─── /         → /opt/travel-platform/frontend/index.html
       │        /api/*     → proxy_pass 127.0.0.1:8001
       │        /picture/* → 静态文件直接托管
       │
       ▼
FastAPI (:8001, systemd: travel-planner.service)
       │
       ├── /api/health              → 健康检查
       ├── /api/planner/pois        → POI 搜索
       ├── /api/planner/itinerary/* → 行程生成（模板+AI）
       ├── /api/ai/ask              → AI 客服
       ├── /api/ai/handoff           → 转人工
       └── /api/ai/handoffs          → 查看转人工列表
              │
              ▼
         DeepSeek API (deepseek-chat)
```

## 技术栈

| 层级 | 技术 | 选择理由 |
|------|------|---------|
| **前端** | 纯 HTML/CSS/JS | 避免构建步骤，零依赖，Nginx 直接托管 |
| **后端** | Python 3.8 + FastAPI | 异步，SSE 原生支持，Python 生态丰富 |
| **LLM** | DeepSeek-V3 (deepseek-chat) | 性价比高，OpenAI 兼容 API |
| **Web 服务器** | Nginx + BT Panel | 宝塔面板预装，配置简单 |
| **部署** | 阿里云 ECS (2核1.8G) | 国内访问快，性价比高 |
| **测试** | pytest + httpx + CI | 20 个测试，GitHub Actions |

## 前端架构

单文件 `index.html` (~680 行)：
- **CSS**：内联样式，无预处理
- **JS**：原生 JavaScript，无框架
  - `P[]` — 13 景点数据 + `imgs[]` 图片路径
  - `N[]` — 12 笔记数据
  - `cardHTML()` — 卡片渲染
  - `openPoint()`/`openNote()` — 详情弹窗 + 图片画廊
  - `askAI()` — AI 客服对话 + 转人工流转
  - `openLightbox()` — 图片全屏查看

## 后端架构

```
services/planner-api/
├── app/
│   ├── main.py              FastAPI 入口
│   ├── api/
│   │   ├── chat.py          POST /api/planner/chat (SSE)
│   │   ├── itinerary.py     GET/POST 行程生成
│   │   ├── poi.py           GET POI 搜索
│   │   └── support.py       AI 客服 + 转人工
│   ├── llm/engine.py        LLM Function Calling
│   ├── services/poi_store.py 50 POI + 行程生成算法
│   └── core/config.py       .env 配置管理
├── tests/                   20 个 pytest 测试
├── requirements.txt
└── .env                     LLM Key
```

## 数据流

```
用户点击"生成行程" 
  → GET /api/planner/itinerary/generate?track=budget&days=3
  → poi_store.py 模板拼装（POI池 + 时间槽 + 费用估算）
  → 返回 JSON: {plan: [...], budget: {total: "¥924"}}
  → 前端渲染行程卡片
```

## 部署配置

| 文件 | 用途 |
|------|------|
| `/etc/systemd/system/travel-planner.service` | 后端自启动 |
| `/www/server/panel/vhost/nginx/travel.conf` | Nginx vhost |
| `/opt/travel-platform/` | 部署目录 |
