# AI Travel Platform — 项目记忆

> 最后更新：2026-06-26

---

## 项目概况

| 项 | 值 |
|----|-----|
| **项目名** | AI入境游一站式定制平台 |
| **代码仓库** | `E:\AI\ly\ai-travel-platform\` |
| **PRD来源** | `C:\Users\junhao.wang\Downloads\一、 产品概述.docx` |
| **开发计划** | `E:\AI\ly\ai-travel-platform-dev-plan.md` (Markdown) |
| **开发计划** | `E:\AI\ly\AI入境游平台_开发计划_V1.0.docx` (Word) |
| **MVP城市** | 重庆 |
| **当前阶段** | Sprint 0+1 完成，Sprint 2 待启动 |

---

## 三阶段路线图

### Phase 1 — MVP (8-10周, 164h)

| Sprint | 内容 | 工时 | 状态 |
|--------|------|------|------|
| Sprint 0 | 项目骨架 + 数据库 + CI/CD | 14h | ✅ |
| Sprint 1 | AI行程规划核心（LLM Function Calling + SSE + 前端） | 44h | ✅ |
| Sprint 2 | POI数据扩展 + AI翻译润色 + 知识图谱雏形 | 34h | ⬜ |
| Sprint 3 | 半自动订单 + Stripe支付 + BOM报价单 | 32h | ⬜ |
| Sprint 4 | AI客服 + 前端整合 + 国际化 + 测试部署 | 40h | ⬜ |

### Phase 2 — V1.0 (8-10周)
- 城市扩展至 8 城、B2B 旅行社入驻、自动分账、知识图谱、多语言

### Phase 3 — V2.0 (6-8周)
- 供应链自动化、AI 多模态营销、实时行程调整、社区 UGC

---

## 技术栈

| 层级 | 技术 | 备注 |
|------|------|------|
| 前端 | Next.js 14 + Tailwind | SWC 兼容性问题，当前用独立 HTML |
| 后端 | Python FastAPI | 异步原生 SSE 支持 |
| LLM | DeepSeek-V3 / GPT-4o | OpenAI 兼容 API |
| 数据库 | PostgreSQL + Redis | docker-compose 配置就绪，MVP 未启用 |
| 搜索 | Elasticsearch | Phase 2 启用 |

---

## 当前架构

```
frontend (localhost:3000)
  ├── public/index.html    ← 当前可用的网站（直连后端 API）
  └── src/app/             ← Next.js 源码（待 SWC 问题修复后启用）
        ├── page.tsx       首页
        └── plan/page.tsx  AI 对话规划页

backend (localhost:8001)
  └── services/planner-api/
        ├── app/main.py            FastAPI 入口
        ├── app/api/chat.py        POST /api/planner/chat (SSE)
        ├── app/api/itinerary.py   GET /api/planner/itinerary/generate
        ├── app/api/poi.py         GET /api/planner/pois
        ├── app/llm/engine.py      LLM Function Calling 引擎
        ├── app/services/poi_store.py  重庆 18 POI + 行程生成算法
        └── app/core/config.py     配置管理
```

---

## 行程生成算法（当前版本）

**类型**：模板拼装算法，非 LLM 生成

**逻辑**：
1. 按 track（premium/budget）筛选 POI 池
2. 每天按固定时间槽填坑：上午景点 → 中午餐厅 → 下午景点/体验 → 晚上夜景
3. 轮询取模避免同一天重复
4. 费用按 `PRICE_TABLE` 均价估算（hotel × 晚数 + meal × 2餐 × 天数 + transport × 天数 + attractions × 天数）
5. 加 5% 平台服务费

**已知局限**：无空间距离校验、无时间合理性判断、轮询机械
**改进方向**：Sprint 2 接入 LLM Function Calling 做智能编排

---

## POI 种子数据（重庆 18 个）

| 类型 | 数量 | 点位 |
|------|------|------|
| attraction | 7 | 洪崖洞、解放碑、磁器口、长江索道、南山一棵树、李子坝、大足石刻 |
| restaurant | 5 | 枇杷园火锅(P)、洞子口老火锅(B)、花市豌杂面(B)、尘香(P)、观音桥好吃街(B) |
| hotel | 4 | 洲际(P)、尼依格罗(P)、亚朵(B)、山城步道青旅(B) |
| experience | 2 | 两江夜游(P)、交通茶馆(B) |

> P=premium专用, B=budget专用

---

## 费用基准

| 模式 | 3天总价 | 酒店/晚 | 餐/顿 | 交通/天 | 景点/天 |
|------|---------|---------|--------|---------|---------|
| Budget | ¥1,386 (~$193) | ¥250 | ¥40 | ¥30 | ¥80 |
| Premium | ¥6,237 (~$866) | ¥1,200 | ¥200 | ¥300 | ¥80 |

---

## 已实现 API 端点

| Method | Path | 状态 |
|--------|------|------|
| GET | /api/health | ✅ |
| GET | /api/planner/pois | ✅ |
| GET | /api/planner/pois/:id | ✅ |
| GET | /api/planner/itinerary/generate | ✅ |
| GET | /api/planner/price-estimate | ✅ |
| GET | /api/planner/transport | ✅ |
| POST | /api/planner/chat (SSE) | ⚙️ 需配 LLM Key |

---

## 关键决策记录

| 日期 | 决策 | 理由 |
|------|------|------|
| 06-25 | 重庆打样 | PRD 建议先 1-2 城市，重庆有辨识度 |
| 06-25 | MVP 用内存存储 | 18 个 POI 不需要 ORM，省复杂度 |
| 06-25 | 模板拼装而非 LLM 生成 | MVP 优先数据可靠性，防 AI 幻觉 |
| 06-26 | 独立 HTML 替代 Next.js | SWC 兼容性问题，功能完全对等 |
| 06-26 | 费用估算用均价 | 无真实酒店 API，用 PRICE_TABLE 常量 |

---

## 下一步（Sprint 2）

1. **POI 扩展** → 从 18 个扩展到 500+，覆盖重庆更多区域
2. **AI 翻译引擎** → 中→英 + 跨文化润色 + 翻译缓存
3. **知识图谱雏形** → POI 间距离/推荐路线关系
4. **LLM 调度上线** → 配 API Key，启用 Function Calling 智能行程编排
