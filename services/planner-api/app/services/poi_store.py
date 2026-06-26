"""POI Store — In-memory data layer for Chongqing MVP

Production would use PostgreSQL + Elasticsearch.
MVP uses curated in-memory data for reliability.
"""

from __future__ import annotations

import json
import os
import random
from typing import Optional

from app.models.schemas import POI, POIType, PriceTrack


# ═══════════════════════════════════════════════════════
# Chongqing Seed POIs — 精心筛选的重庆数据
# ═══════════════════════════════════════════════════════

CHONGQING_POIS: list[dict] = [
    # ── Attractions ──────────────────────────────────
    {
        "id": "cq_hongya_cave",
        "name_zh": "洪崖洞",
        "name_en": "Hongya Cave",
        "city": "chongqing",
        "type": "attraction",
        "lat": 29.5647, "lng": 106.5833,
        "tags": ["夜景", "巴渝建筑", "打卡", "免费"],
        "description_zh": "依山而建的吊脚楼群，夜晚灯火璀璨如千与千寻场景",
        "description_en": "Stilted buildings clinging to the cliffside, stunningly illuminated at night — often compared to Spirited Away",
        "price_range": "免费",
        "opening_hours": "全天（夜景19:00-23:00最佳）",
        "tips": ["周末人极多，建议工作日去", "最佳拍照点在对岸南滨路", "晚上10点后灯会逐步关"],
        "best_photo_spot": "千厮门大桥上或对岸南滨路",
        "track": "both",
        "rating": 4.5,
    },
    {
        "id": "cq_jiefangbei",
        "name_zh": "解放碑",
        "name_en": "Jiefangbei CBD",
        "city": "chongqing",
        "type": "attraction",
        "lat": 29.5603, "lng": 106.5767,
        "tags": ["商圈", "地标", "购物", "免费"],
        "description_zh": "重庆最繁华的商业中心，抗战胜利纪功碑所在地",
        "description_en": "Chongqing's busiest commercial hub, home to the Victory Monument",
        "price_range": "免费",
        "opening_hours": "全天",
        "tips": ["周边八一好吃街是美食天堂", "各大奢侈品和快时尚品牌齐全"],
        "best_photo_spot": "解放碑正面广场",
        "track": "both",
        "rating": 4.3,
    },
    {
        "id": "cq_ciqikou",
        "name_zh": "磁器口古镇",
        "name_en": "Ciqikou Ancient Town",
        "city": "chongqing",
        "type": "attraction",
        "lat": 29.5813, "lng": 106.4527,
        "tags": ["古镇", "美食", "手工艺", "免费"],
        "description_zh": "千年古镇，青石板路蜿蜒，陈麻花和毛血旺的发源地",
        "description_en": "A thousand-year-old riverside town with winding cobblestone lanes, famous for Chen's Mahua and Mao Xue Wang",
        "price_range": "免费",
        "opening_hours": "全天（商铺10:00-21:00）",
        "tips": ["周末人挤人，建议早上去", "必尝陈麻花（排队最长那家就是）", "小巷子里有隐藏茶馆"],
        "best_photo_spot": "主街尽头江边观景台",
        "track": "both",
        "rating": 4.4,
    },
    {
        "id": "cq_cableway",
        "name_zh": "长江索道",
        "name_en": "Yangtze River Cableway",
        "city": "chongqing",
        "type": "attraction",
        "lat": 29.5619, "lng": 106.5847,
        "tags": ["交通", "体验", "江景", "地标"],
        "description_zh": "万里长江第一条空中走廊，4分钟飞渡长江",
        "description_en": "The first aerial tramway across the Yangtze — a 4-minute flight over the river",
        "price_range": "单程20元，往返30元",
        "opening_hours": "07:30-22:30",
        "tips": ["傍晚坐最出片", "北站（新华路）排队人多，南站（上新街）人少很多", "刷重庆交通卡半价"],
        "best_photo_spot": "索道车厢内靠窗位",
        "track": "both",
        "rating": 4.6,
    },
    {
        "id": "cq_nanshan_tree",
        "name_zh": "南山一棵树观景台",
        "name_en": "Nanshan Tree Viewing Deck",
        "city": "chongqing",
        "type": "attraction",
        "lat": 29.5444, "lng": 106.6078,
        "tags": ["夜景", "观景台", "全景"],
        "description_zh": "俯瞰渝中半岛夜景的最佳位置，两江交汇尽收眼底",
        "description_en": "The best panoramic night view of Yuzhong Peninsula — where two rivers meet",
        "price_range": "门票30元",
        "opening_hours": "09:00-22:30",
        "tips": ["一定要晚上去！白天效果打五折", "带三脚架拍夜景", "山上比市区凉快3-5度"],
        "best_photo_spot": "观景台最高层",
        "track": "both",
        "rating": 4.7,
    },
    {
        "id": "cq_liziba",
        "name_zh": "李子坝轻轨穿楼",
        "name_en": "Liziba Light Rail Through Building",
        "city": "chongqing",
        "type": "attraction",
        "lat": 29.5534, "lng": 106.5356,
        "tags": ["网红", "交通", "打卡", "免费"],
        "description_zh": "轻轨2号线穿楼而过，重庆8D魔幻城市代表作",
        "description_en": "Light Rail Line 2 passes directly through a residential building — the ultimate embodiment of Chongqing's 8D magic",
        "price_range": "免费（轻轨票价2-7元）",
        "opening_hours": "全天",
        "tips": ["最佳拍摄点在楼下观景平台", "建议亲自坐一趟2号线体验", "上午光线方向更适合拍照"],
        "best_photo_spot": "李子坝观景平台",
        "track": "both",
        "rating": 4.5,
    },
    {
        "id": "cq_dazu",
        "name_zh": "大足石刻",
        "name_en": "Dazu Rock Carvings",
        "city": "chongqing",
        "type": "attraction",
        "lat": 29.7384, "lng": 105.7084,
        "tags": ["UNESCO", "文化", "历史", "世界遗产"],
        "description_zh": "世界文化遗产，唐宋石刻艺术巅峰，佛教文化瑰宝",
        "description_en": "UNESCO World Heritage — peak of Tang-Song rock carving art, a Buddhist cultural treasure",
        "price_range": "门票135元",
        "opening_hours": "08:30-17:30",
        "tips": ["离市区约2小时车程，需留一整天", "请讲解员体验翻倍", "宝顶山是精华核心区"],
        "best_photo_spot": "宝顶山千手观音像前",
        "track": "both",
        "rating": 4.8,
    },

    # ── Restaurants ──────────────────────────────────
    {
        "id": "cq_nanshan_hotpot",
        "name_zh": "枇杷园火锅（南山总店）",
        "name_en": "Pipa Yuan Hotpot (Nanshan)",
        "city": "chongqing",
        "type": "restaurant",
        "lat": 29.5389, "lng": 106.6122,
        "tags": ["火锅", "山景", "网红"],
        "description_zh": "整座山都是火锅桌！600桌同时沸腾的壮观场面",
        "description_en": "An entire hillside of hotpot tables — 600 tables boiling simultaneously",
        "price_range": "人均120元",
        "opening_hours": "11:00-23:00",
        "tips": ["周末排队2小时起", "坐半山腰位置风景最好", "必点：毛肚、鸭肠、耗儿鱼"],
        "track": "premium",
        "rating": 4.3,
    },
    {
        "id": "cq_dongzikou",
        "name_zh": "洞子口老火锅",
        "name_en": "Dongzikou Old Hotpot",
        "city": "chongqing",
        "type": "restaurant",
        "lat": 29.5612, "lng": 106.5701,
        "tags": ["火锅", "老字号", "本地人"],
        "description_zh": "藏在防空洞里的老火锅，本地人从小吃到大",
        "description_en": "Old-school hotpot hidden in an air-raid shelter — where locals have eaten since childhood",
        "price_range": "人均60元",
        "opening_hours": "11:00-02:00",
        "tips": ["环境简陋但味道绝了", "微辣=外地人的特辣", "必点：嫩牛肉、贡菜"],
        "track": "budget",
        "rating": 4.6,
    },
    {
        "id": "cq_xiaomian",
        "name_zh": "花市豌杂面",
        "name_en": "Huashi Pea & Minced Pork Noodles",
        "city": "chongqing",
        "type": "restaurant",
        "lat": 29.5598, "lng": 106.5783,
        "tags": ["小面", "早餐", "老字号"],
        "description_zh": "重庆小面界的天花板，豌豆软糯肉酱浓香",
        "description_en": "The pinnacle of Chongqing noodles — soft peas and fragrant minced pork",
        "price_range": "人均15元",
        "opening_hours": "06:00-14:00",
        "tips": ["只做早餐和午餐，下午去就没了", "豌杂面+煎蛋=标配", "二两就够了，别点多"],
        "track": "budget",
        "rating": 4.7,
    },
    {
        "id": "cq_chenmapo",
        "name_zh": "尘香·新派川菜",
        "name_en": "Chenxiang Modern Sichuan",
        "city": "chongqing",
        "type": "restaurant",
        "lat": 29.5567, "lng": 106.5722,
        "tags": ["川菜", "精致", "宴请"],
        "description_zh": "黑珍珠一钻，传统川菜的精致演绎，环境雅致",
        "description_en": "Black Pearl one-diamond — refined traditional Sichuan cuisine in elegant setting",
        "price_range": "人均300元",
        "opening_hours": "11:30-14:00, 17:30-21:30",
        "tips": ["需提前3天预订", "推荐：开水白菜、宫保虾球", "适合商务宴请或纪念日"],
        "track": "premium",
        "rating": 4.6,
    },
    {
        "id": "cq_guanyinqiao_street",
        "name_zh": "观音桥好吃街",
        "name_en": "Guanyinqiao Food Street",
        "city": "chongqing",
        "type": "restaurant",
        "lat": 29.5778, "lng": 106.5311,
        "tags": ["小吃", "夜市", "烟火气"],
        "description_zh": "重庆最接地气的美食街，酸辣粉、烤脑花、冰粉凉虾应有尽有",
        "description_en": "Chongqing's most down-to-earth food street — spicy noodles, grilled brain, iced jelly",
        "price_range": "人均30-50元",
        "opening_hours": "10:00-23:00",
        "tips": ["空腹去！", "必吃：好又来酸辣粉、山城汤圆", "晚上最热闹"],
        "track": "budget",
        "rating": 4.4,
    },

    # ── Hotels ───────────────────────────────────────
    {
        "id": "cq_raffles",
        "name_zh": "重庆来福士洲际酒店",
        "name_en": "InterContinental Chongqing Raffles City",
        "city": "chongqing",
        "type": "hotel",
        "lat": 29.5633, "lng": 106.5867,
        "tags": ["奢华", "江景", "天际线"],
        "description_zh": "来福士水晶连廊内，250米高空酒店，俯瞰两江交汇",
        "description_en": "Inside the Raffles City Crystal Skybridge at 250m — overlooks the confluence of two rivers",
        "price_range": "¥1,200-3,000/晚",
        "tips": ["水晶连廊是酒店专属", "江景房必选（城景房看不到江）"],
        "track": "premium",
        "rating": 4.8,
    },
    {
        "id": "cq_niccolo",
        "name_zh": "重庆尼依格罗酒店",
        "name_en": "Niccolo Chongqing",
        "city": "chongqing",
        "type": "hotel",
        "lat": 29.5817, "lng": 106.5464,
        "tags": ["奢华", "天际线", "设计"],
        "description_zh": "IFS国金中心62层高空酒店，现代艺术风格",
        "description_en": "62nd floor of IFS — modern art-inspired luxury with panoramic skyline views",
        "price_range": "¥1,000-2,500/晚",
        "tips": ["62层大堂本身就是打卡点", "早餐丰盛，推荐班尼迪克蛋"],
        "track": "premium",
        "rating": 4.7,
    },
    {
        "id": "cq_hi_jiefangbei",
        "name_zh": "重庆解放碑亚朵酒店",
        "name_en": "Atour Hotel Jiefangbei",
        "city": "chongqing",
        "type": "hotel",
        "lat": 29.5583, "lng": 106.5750,
        "tags": ["舒适", "性价比", "位置好"],
        "description_zh": "解放碑核心区域，步行可达洪崖洞/长江索道",
        "description_en": "In the heart of Jiefangbei, walking distance to Hongya Cave and the cableway",
        "price_range": "¥350-600/晚",
        "tips": ["免费洗衣房", "竹居书吧看书免费", "提前订周末房比较紧张"],
        "track": "budget",
        "rating": 4.5,
    },
    {
        "id": "cq_qinglv",
        "name_zh": "重庆山城步道青年旅舍",
        "name_en": "Shancheng Trail Hostel",
        "city": "chongqing",
        "type": "hotel",
        "lat": 29.5561, "lng": 106.5689,
        "tags": ["青旅", "背包客", "社交"],
        "description_zh": "山城步道旁，老重庆味道的青旅，屋顶露台看江景",
        "description_en": "Hostel near the Shancheng Trail with old Chongqing charm, rooftop river views",
        "price_range": "¥60-150/晚",
        "tips": ["公共区域氛围好，容易结识旅伴", "建议提前预订私人间"],
        "track": "budget",
        "rating": 4.3,
    },

    # ── Experiences ──────────────────────────────────
    {
        "id": "cq_night_cruise",
        "name_zh": "两江夜游",
        "name_en": "Two Rivers Night Cruise",
        "city": "chongqing",
        "type": "experience",
        "lat": 29.5642, "lng": 106.5861,
        "tags": ["游船", "夜景", "浪漫"],
        "description_zh": "乘船游览长江与嘉陵江交汇，两岸灯火辉煌",
        "description_en": "Cruise the confluence of Yangtze and Jialing rivers surrounded by glittering city lights",
        "price_range": "¥128-188/人",
        "opening_hours": "19:30-22:00（多班次）",
        "tips": ["选朝天门码头上船最方便", "VIP层加50元但视野确实好", "周末班次需提前1天订票"],
        "track": "premium",
        "rating": 4.4,
    },
    {
        "id": "cq_teahouse",
        "name_zh": "交通茶馆",
        "name_en": "Jiaotong Teahouse",
        "city": "chongqing",
        "type": "experience",
        "lat": 29.5478, "lng": 106.5433,
        "tags": ["茶馆", "文化", "市井"],
        "description_zh": "重庆最老的茶馆，30年未变，老茶客打牌摆龙门阵",
        "description_en": "Chongqing's oldest teahouse — unchanged for 30 years, old-timers playing cards and chatting",
        "price_range": "茶¥8-15/杯",
        "tips": ["自带零食，茶馆只卖茶", "拍照前先和老人家打个招呼", "下午3点后最热闹"],
        "track": "budget",
        "rating": 4.5,
    },
]

# Transport matrix (origin -> destination -> options)
TRANSPORT_MATRIX = {
    "解放碑": {
        "洪崖洞": [{"mode": "walk", "duration": "10min", "cost": "免费", "tip": "步行穿过沧白路即到"}],
        "长江索道": [{"mode": "walk", "duration": "8min", "cost": "免费", "tip": "新华路站步行可达"}],
        "磁器口": [{"mode": "metro", "duration": "30min", "cost": "3元", "tip": "1号线磁器口站下"}],
        "南山一棵树": [{"mode": "taxi", "duration": "25min", "cost": "约30元", "tip": "过长江大桥后上南山"}],
        "李子坝": [{"mode": "metro", "duration": "12min", "cost": "2元", "tip": "2号线李子坝站下"}],
    },
    "洪崖洞": {
        "解放碑": [{"mode": "walk", "duration": "10min", "cost": "免费"}],
        "长江索道": [{"mode": "walk", "duration": "15min", "cost": "免费", "tip": "沿滨江路走到新华路"}],
    },
    "磁器口": {
        "解放碑": [{"mode": "metro", "duration": "30min", "cost": "3元", "tip": "1号线较场口站方向"}],
        "李子坝": [{"mode": "metro", "duration": "20min", "cost": "2元", "tip": "1号线转2号线"}],
    },
}

PRICE_TABLE = {
    "hotel_premium": {"per_night": 1200, "currency": "CNY"},
    "hotel_budget": {"per_night": 250, "currency": "CNY"},
    "meal_premium": {"per_meal": 200, "currency": "CNY"},
    "meal_budget": {"per_meal": 40, "currency": "CNY"},
    "transport_premium": {"per_day": 300, "currency": "CNY", "desc": "包车/出租车"},
    "transport_budget": {"per_day": 30, "currency": "CNY", "desc": "地铁+公交"},
    "attraction_avg": {"per_day": 80, "currency": "CNY"},
    "service_fee": 0.05,  # 5% platform fee
}


class POIStore:
    """In-memory POI store — MVP version"""

    def __init__(self):
        self.pois: list[dict] = CHONGQING_POIS
        self._poi_dict: dict[str, dict] = {p["id"]: p for p in self.pois}

    async def seed(self) -> int:
        """Called on startup"""
        return len(self.pois)

    async def search_poi(
        self,
        query: str,
        poi_type: str | None = None,
        track: str = "both",
        limit: int = 5,
    ) -> dict:
        """Search POIs by keyword"""
        q = query.lower()
        results = []
        for p in self.pois:
            if poi_type and p["type"] != poi_type:
                continue
            # Track filter
            if track == "premium" and p.get("track") == "budget":
                continue
            if track == "budget" and p.get("track") == "premium":
                continue
            # Simple keyword matching
            match = (
                q in p["name_zh"]
                or q in p["name_en"].lower()
                or q in p["description_zh"]
                or any(q in t.lower() for t in p.get("tags", []))
            )
            if match or not q:  # empty query returns all
                results.append({
                    "id": p["id"],
                    "name_zh": p["name_zh"],
                    "name_en": p["name_en"],
                    "type": p["type"],
                    "lat": p["lat"],
                    "lng": p["lng"],
                    "tags": p["tags"],
                    "price_range": p["price_range"],
                    "rating": p["rating"],
                    "track": p.get("track", "both"),
                    "description_zh": p["description_zh"][:120] + "...",
                    "description_en": p["description_en"][:120] + "...",
                })
        return {
            "query": query,
            "count": min(len(results), limit),
            "results": results[:limit],
        }

    async def search_hotel(
        self,
        area: str | None = None,
        track: str = "budget",
        limit: int = 3,
    ) -> dict:
        """Search hotels"""
        results = []
        for p in self.pois:
            if p["type"] != "hotel":
                continue
            if p.get("track") != track and p.get("track") != "both":
                continue
            if area and area not in p["name_zh"] and area not in p["description_zh"]:
                continue
            results.append({
                "id": p["id"],
                "name_zh": p["name_zh"],
                "name_en": p["name_en"],
                "price_range": p["price_range"],
                "rating": p["rating"],
                "tags": p["tags"],
                "track": p.get("track"),
            })
        return {
            "track": track,
            "count": min(len(results), limit),
            "results": results[:limit],
        }

    async def get_transport(
        self,
        origin: str,
        destination: str,
        mode: str = "metro",
    ) -> dict:
        """Get transport options between two locations"""
        options = TRANSPORT_MATRIX.get(origin, {}).get(destination, [])
        if not options:
            # Reverse lookup
            options = TRANSPORT_MATRIX.get(destination, {}).get(origin, [])
        if not options:
            options = [{
                "mode": mode,
                "duration": "约30分钟",
                "cost": f"约{30 if mode == 'taxi' else '3'}元",
                "tip": "建议使用高德地图导航",
            }]
        return {
            "origin": origin,
            "destination": destination,
            "options": options,
        }

    async def calculate_price(
        self,
        items: list[dict],
        track: str = "budget",
        days: int = 3,
    ) -> dict:
        """Estimate trip cost"""
        hotel_per_night = PRICE_TABLE["hotel_premium" if track == "premium" else "hotel_budget"]["per_night"]
        meal_per = PRICE_TABLE["meal_premium" if track == "premium" else "meal_budget"]["per_meal"]
        transport_per_day = PRICE_TABLE["transport_premium" if track == "premium" else "transport_budget"]["per_day"]
        attraction_per_day = PRICE_TABLE["attraction_avg"]["per_day"]
        service_fee = PRICE_TABLE["service_fee"]

        subtotal = (
            hotel_per_night * days
            + meal_per * 2 * days  # 2 meals/day
            + transport_per_day * days
            + attraction_per_day * days
        )
        fee = round(subtotal * service_fee)
        total = subtotal + fee

        return {
            "track": track,
            "days": days,
            "breakdown": {
                "hotel": f"¥{hotel_per_night} x {days}晚 = ¥{hotel_per_night * days}",
                "meals": f"¥{meal_per} x 2餐 x {days}天 = ¥{meal_per * 2 * days}",
                "transport": f"¥{transport_per_day} x {days}天 = ¥{transport_per_day * days}",
                "attractions": f"约¥{attraction_per_day} x {days}天 = ¥{attraction_per_day * days}",
            },
            "subtotal": f"¥{subtotal}",
            "service_fee_pct": f"{int(service_fee * 100)}%",
            "service_fee": f"¥{fee}",
            "total": f"¥{total}",
            "total_usd": f"${round(total / 7.2)}",
        }

    async def generate_itinerary_struct(
        self,
        days: int = 3,
        track: str = "budget",
        preferences: str = "",
        selected_pois: list[str] = [],
    ) -> dict:
        """Generate a structured itinerary using seed data"""
        # Pick POIs based on track
        track_filter = track if track in ("premium", "budget") else "both"
        attractions = [p for p in self.pois if p["type"] == "attraction" and p.get("track") in (track_filter, "both")]
        restaurants = [p for p in self.pois if p["type"] == "restaurant" and p.get("track") in (track_filter, "both")]
        hotels = [p for p in self.pois if p["type"] == "hotel" and p.get("track") in (track_filter, "both")]
        experiences = [p for p in self.pois if p["type"] == "experience" and p.get("track") in (track_filter, "both")]

        plan = []
        for day in range(1, days + 1):
            items = []

            # Morning: attraction
            if attractions:
                a = attractions[day % len(attractions)]
                items.append({
                    "time": "09:00-12:00",
                    "poi_name_zh": a["name_zh"],
                    "poi_name_en": a["name_en"],
                    "poi_id": a["id"],
                    "activity": f"游览{a['name_zh']}",
                    "transport": "地铁",
                    "duration": "3h",
                    "cost_estimate": a["price_range"],
                    "tips": a.get("tips", [])[:2],
                })

            # Lunch: restaurant
            if restaurants:
                r = restaurants[day % len(restaurants)]
                items.append({
                    "time": "12:00-13:30",
                    "poi_name_zh": r["name_zh"],
                    "poi_name_en": r["name_en"],
                    "poi_id": r["id"],
                    "activity": f"午餐：{r['name_zh']}",
                    "transport": "步行",
                    "duration": "1.5h",
                    "cost_estimate": r["price_range"],
                    "tips": r.get("tips", [])[:1],
                })

            # Afternoon: second attraction or experience
            if day == 2 and experiences:
                e = experiences[0]
                items.append({
                    "time": "14:00-16:00",
                    "poi_name_zh": e["name_zh"],
                    "poi_name_en": e["name_en"],
                    "poi_id": e["id"],
                    "activity": f"体验{e['name_zh']}",
                    "transport": "步行+地铁",
                    "duration": "2h",
                    "cost_estimate": e.get("price_range", ""),
                    "tips": e.get("tips", [])[:1],
                })
            elif len(attractions) > day:
                a2 = attractions[(day + 1) % len(attractions)]
                items.append({
                    "time": "14:00-17:00",
                    "poi_name_zh": a2["name_zh"],
                    "poi_name_en": a2["name_en"],
                    "poi_id": a2["id"],
                    "activity": f"游览{a2['name_zh']}",
                    "transport": "地铁/打车",
                    "duration": "3h",
                    "cost_estimate": a2["price_range"],
                    "tips": a2.get("tips", [])[:1],
                })

            # Evening: night view or dinner
            if day < days:
                night_spot = [p for p in attractions if "夜景" in p.get("tags", [])]
                if night_spot:
                    n = night_spot[day % len(night_spot)]
                    items.append({
                        "time": "18:00-21:00",
                        "poi_name_zh": n["name_zh"],
                        "poi_name_en": n["name_en"],
                        "poi_id": n["id"],
                        "activity": f"晚餐+赏夜景：{n['name_zh']}",
                        "transport": "地铁",
                        "duration": "3h",
                        "cost_estimate": n["price_range"],
                        "tips": n.get("tips", [])[:2],
                    })

            plan.append({
                "day": day,
                "date": f"Day {day}",
                "title_zh": ["初探山城", "深度漫游", "告别重庆"][day - 1] if day <= 3 else f"第{day}天",
                "title_en": ["First Taste of the Mountain City", "Deep Dive", "Farewell Chongqing"][day - 1] if day <= 3 else f"Day {day}",
                "items": items,
            })

        # Calculate budget
        cost = await self.calculate_price([], track, days)

        return {
            "city": "chongqing",
            "track": track,
            "days": days,
            "plan": plan,
            "budget": cost,
        }

    async def get_all_pois(self) -> list[dict]:
        return [{
            "id": p["id"],
            "name_zh": p["name_zh"],
            "name_en": p["name_en"],
            "type": p["type"],
            "lat": p["lat"],
            "lng": p["lng"],
            "tags": p["tags"],
            "price_range": p["price_range"],
            "track": p.get("track", "both"),
            "rating": p["rating"],
        } for p in self.pois]

    async def get_poi_detail(self, poi_id: str) -> dict | None:
        p = self._poi_dict.get(poi_id)
        if not p:
            return None
        return {k: v for k, v in p.items()}


# Singleton
_store: POIStore | None = None


def get_store() -> POIStore:
    global _store
    if _store is None:
        _store = POIStore()
    return _store
