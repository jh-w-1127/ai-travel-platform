# AI Travel Platform — 项目记忆

> ⚠️ 本文档已由 `../ai-travel-platform-dev-plan.md` 取代，此处仅保留历史记录。
> 最新进度、待做清单和偏离分析请查阅开发计划。

## 项目概况

| 项 | 值 |
|----|-----|
| **项目名** | AI入境游一站式定制平台 |
| **MVP城市** | 重庆 |
| **线上地址** | https://mmyou.top |
| **当前阶段** | Sprint 2 部分完成 + Sprint 4 部分完成 |
| **LLM** | DeepSeek-V3 已接入，行程规划 + AI客服均运行中 |
| **POI** | 50 个（景点/餐厅/酒店/体验/交通） |
| **服务器** | 阿里云 ECS (47.250.175.170) — Nginx + systemd |

---

## 关键决策记录

| 日期 | 决策 | 理由 |
|------|------|------|
| 06-25 | 重庆打样 | PRD 建议先 1-2 城市，重庆有辨识度 |
| 06-25 | MVP 用内存存储 | MVP 阶段不需要 ORM |
| 06-26 | 独立 HTML 替代 Next.js | SWC 兼容性问题，现用纯 HTML |
| 07-09 | DeepSeek-V3 接入 | AI行程计划 + AI客服所需 |
| 07-09 | 服务器部署 | 阿里云 + Nginx + systemd |
| 07-10 | AI客服转人工 | 支持 handoff 流转 + admin 后台 |
| 07-16 | 域名 mmyou.top | DNS A 记录指向服务器 IP |

*历史 Sprint 详情见 `../ai-travel-platform-dev-plan.md`*
