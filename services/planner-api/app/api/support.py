"""AI客服 API — knowledge-enhanced Q&A"""

import json
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.core.config import settings

router = APIRouter()


class AskRequest(BaseModel):
    question: str
    context: str = ""  # optional: user's current itinerary context


# Simple knowledge base for fallback (when LLM is not available)
KB = {
    "签证": "大多数国家可享受144小时过境免签（通过重庆江北机场入境）。护照有效期需超过6个月。建议出发前查看 china-entry.gov.cn 最新政策。",
    "visa": "Most nationalities enjoy 144-hour transit visa-free through Chongqing Jiangbei Airport. Passport must be valid for 6+ months. Check china-entry.gov.cn for latest.",
    "付款": "重庆支持支付宝国际版（Alipay TourPass）绑定Visa/Mastercard。现金在大部分地方通用。建议：支付宝 + 随身¥300-500现金。4-5星酒店接受信用卡。",
    "pay": "Alipay TourPass supports Visa/Mastercard. Cash works everywhere. Bring ¥300-500 cash + Alipay. 4-5 star hotels accept credit cards.",
    "交通": "重庆地铁有英文标识，单程¥2-7元。办交通卡（¥25押金，索道半价）。打车起步¥10。Apple Maps在中国可用。",
    "transport": "Chongqing metro has English signs, ¥2-7 per ride. Get a transport card (¥25 deposit, cableway 50% off). Taxi starts at ¥10. Apple Maps works in China.",
    "行李": "全年必备：平底鞋/运动鞋（爬坡！）。夏季：轻薄衣物+防晒霜+雨伞。冬季：薄羽绒+围巾。全年：充电宝、纸巾。",
    "pack": "Year-round: comfortable walking shoes (lots of stairs!). Summer: light clothes + sunscreen + umbrella. Winter: light down jacket + scarf. Always: power bank + tissues.",
    "天气": "夏季（6-9月）25-38°C湿热多阵雨。冬季（12-2月）5-12°C湿冷。最佳季节：3-5月和10-11月，15-25°C舒适。",
    "weather": "Summer (Jun-Sep): 25-38°C, hot & humid. Winter (Dec-Feb): 5-12°C, cold & damp. Best: Mar-May & Oct-Nov, 15-25°C.",
    "安全": "重庆非常安全。紧急电话：110（警察）、120（急救）。重庆江北和睦家医院有英文服务。建议保存酒店名片（有中文地址）。",
    "safe": "Chongqing is very safe. Emergency: 110 (police), 120 (ambulance). Chongqing United Family Hospital has English service. Keep hotel business card.",
    "行程推荐": "经典3天：Day1 解放碑→洪崖洞→李子坝→长江索道→南山夜景；Day2 磁器口→鹅岭→两江夜游；Day3 大足石刻一日游。更多可去「行程计划」页签定制！",
    "recommend": "Classic 3-day: Day1 Jiefangbei→Hongya Cave→Liziba→Cableway→Nanshan; Day2 Ciqikou→Eling→Night Cruise; Day3 Dazu Rock Carvings. Use Trip Planner tab!",
    "火锅": "重庆火锅是国家级非遗！推荐：洞子口老火锅（防空洞体验，人均¥60）、枇杷园（整座山都是火锅桌，人均¥120）。必点：毛肚、鸭肠、耗儿鱼、嫩牛肉。解辣：唯怡豆奶+红糖冰粉。",
    "hotpot": "Chongqing hotpot is National Intangible Heritage! Try: Dongzikou (bomb shelter, ¥60/person), Pipa Yuan (mountain of hotpot, ¥120/person). Must-order: tripe, duck intestine, beef. Cool down: Weiyi soy milk + iced jelly.",
}


@router.post("/ai/ask")
async def ai_ask(req: AskRequest):
    """AI-powered Q&A for travel support.
    Uses LLM if configured, falls back to keyword matching."""
    
    q = req.question.lower()
    
    # Try keyword matching: does user question contain any KB key?
    for key, answer in KB.items():
        if key.lower() in q or q in key.lower():
            return {"answer": answer, "source": "knowledge_base"}
    
    # Try LLM if configured
    if settings.llm_api_key and settings.llm_api_key != "sk-placeholder":
        try:
            import httpx
            async with httpx.AsyncClient(timeout=30.0) as client:
                resp = await client.post(
                    f"{settings.llm_base_url}/chat/completions",
                    headers={
                        "Authorization": f"Bearer {settings.llm_api_key}",
                        "Content-Type": "application/json",
                    },
                    json={
                        "model": settings.llm_model,
                        "messages": [
                            {"role": "system", "content": "你是重庆旅行助手。用简洁友好的中文回答。如果问题与旅行无关，礼貌引导。回答控制在100字以内。"},
                            {"role": "user", "content": req.question},
                        ],
                        "temperature": 0.7,
                        "max_tokens": 300,
                    },
                )
                data = resp.json()
                answer = data["choices"][0]["message"]["content"]
                return {"answer": answer, "source": "ai"}
        except Exception:
            pass
    
    # Ultimate fallback
    return {
        "answer": "关于这个问题，建议查看我们的「景点」和「笔记」页签了解更多重庆攻略。也可以试试问：签证、付款、交通、行李、天气、行程推荐、安全。",
        "source": "fallback"
    }
