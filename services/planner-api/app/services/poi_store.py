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

    # ══ Extended Attractions (from content library) ══
    {
        "id": "cq_baidi_city",
        "name_zh": "白帝城",
        "name_en": "Baidi City & Qutang Gorge",
        "city": "chongqing",
        "type": "attraction",
        "lat": 31.0436, "lng": 109.5711,
        "tags": ["三国", "诗歌", "三峡", "10元背景"],
        "description_zh": "三峡入口，10元人民币背景夔门所在地，刘备托孤处",
        "description_en": "Entrance to Three Gorges, the scene on ¥10 note, where Liu Bei entrusted his kingdom",
        "price_range": "¥100",
        "opening_hours": "08:00-17:30",
        "tips": ["备好10元纸币拍同框", "建议跟武隆/巫山打包成2-3天行程"],
        "track": "both",
        "rating": 4.6,
    },
    {
        "id": "cq_wushan_gorges",
        "name_zh": "巫山小三峡",
        "name_en": "Lesser Three Gorges",
        "city": "chongqing",
        "type": "attraction",
        "lat": 31.0756, "lng": 109.8789,
        "tags": ["峡谷", "游船", "悬棺", "翡翠水"],
        "description_zh": "大宁河峡谷，翡翠绿水，千年悬棺之谜",
        "description_en": "Jade-green water winding through gorges, 2000-year-old hanging coffins mystery",
        "price_range": "¥150",
        "opening_hours": "08:00-17:00",
        "tips": ["10-11月红叶季最美", "船程约4小时，带薄外套"],
        "track": "both",
        "rating": 4.5,
    },
    {
        "id": "cq_peach_blossom",
        "name_zh": "酉阳桃花源",
        "name_en": "Peach Blossom Spring",
        "city": "chongqing",
        "type": "attraction",
        "lat": 28.8417, "lng": 108.7681,
        "tags": ["世外桃源", "溶洞", "土家族", "陶渊明"],
        "description_zh": "穿过溶洞进入四面环山的世外桃源，与陶渊明笔下一致",
        "description_en": "Walk through a cave into a hidden valley — exactly as described by poet Tao Yuanming",
        "price_range": "¥100",
        "opening_hours": "08:00-17:30",
        "tips": ["3-4月春花开最美", "洞穴→山谷的揭示体验是最大亮点"],
        "track": "both",
        "rating": 4.3,
    },
    {
        "id": "cq_eguang_park",
        "name_zh": "鹅岭公园",
        "name_en": "Eling Park",
        "city": "chongqing",
        "type": "attraction",
        "lat": 29.5514, "lng": 106.5439,
        "tags": ["公园", "全景", "免费", "民国"],
        "description_zh": "重庆最老的城市公园，瞰胜楼看两江全景",
        "description_en": "Chongqing's oldest city park, panoramic views from Kansheng Pavilion",
        "price_range": "免费",
        "opening_hours": "06:00-22:00",
        "tips": ["日落前1小时到最佳", "瞰胜楼加收5元但值得"],
        "track": "both",
        "rating": 4.3,
    },
    {
        "id": "cq_shancheng_trail",
        "name_zh": "山城步道（第三步道）",
        "name_en": "Shancheng Trail (Third Trail)",
        "city": "chongqing",
        "type": "attraction",
        "lat": 29.5539, "lng": 106.5708,
        "tags": ["徒步", "老重庆", "悬崖", "免费"],
        "description_zh": "沿着渝中半岛悬崖修建的步道，途经法国领事馆旧址",
        "description_en": "Cliffside walking trail through old Chongqing, passing the former French Consulate",
        "price_range": "免费",
        "opening_hours": "全天",
        "tips": ["全程约2小时", "穿运动鞋", "沿途有茶馆可歇脚"],
        "track": "both",
        "rating": 4.4,
    },
    {
        "id": "cq_nanbin_road",
        "name_zh": "南滨路",
        "name_en": "Nanbin Road",
        "city": "chongqing",
        "type": "attraction",
        "lat": 29.5556, "lng": 106.5864,
        "tags": ["江景", "散步", "免费", "夜景"],
        "description_zh": "南岸沿江景观大道，对岸看渝中半岛天际线的最佳位置",
        "description_en": "Riverside promenade with the best views of Yuzhong Peninsula skyline",
        "price_range": "免费",
        "opening_hours": "全天",
        "tips": ["傍晚到深夜最佳", "沿路有很多江景餐厅和酒吧"],
        "track": "both",
        "rating": 4.5,
    },
    {
        "id": "cq_raffles_city",
        "name_zh": "来福士广场",
        "name_en": "Raffles City Chongqing",
        "city": "chongqing",
        "type": "attraction",
        "lat": 29.5628, "lng": 106.5853,
        "tags": ["建筑", "购物", "打卡", "地标"],
        "description_zh": "朝天门250米高空水晶连廊，重庆新地标",
        "description_en": "250m crystal skybridge at Chaotianmen — Chongqing's new landmark",
        "price_range": "商场免费 / 观景台¥180",
        "opening_hours": "10:00-22:00",
        "tips": ["观景台需提前预约", "商场内餐饮选择多"],
        "track": "premium",
        "rating": 4.5,
    },

    # ══ Extended Restaurants ══
    {
        "id": "cq_nanshan_hotpot",
        "name_zh": "枇杷园火锅（南山）",
        "name_en": "Pipa Yuan Hotpot (Nanshan)",
        "city": "chongqing",
        "type": "restaurant",
        "lat": 29.5183, "lng": 106.6125,
        "tags": ["火锅", "夜景", "山景", "打卡"],
        "description_zh": "整座山都是火锅桌！南山枇杷园，上千桌火锅依山而建",
        "description_en": "An entire mountain of hotpot tables — 1000+ tables built into the Nanshan hillside",
        "price_range": "¥100-150/人",
        "tips": ["18:00前到能抢到景观位", "山上凉快，夏天都不用空调"],
        "track": "premium",
        "rating": 4.5,
    },
    {
        "id": "cq_dongzikou_hotpot",
        "name_zh": "洞子口老火锅",
        "name_en": "Dongzikou Old Hotpot",
        "city": "chongqing",
        "type": "restaurant",
        "lat": 29.5556, "lng": 106.5639,
        "tags": ["火锅", "防空洞", "老字号", "市井"],
        "description_zh": "在二战防空洞里吃火锅，体验最地道的重庆",
        "description_en": "Hotpot in a WWII bomb shelter — the most authentic Chongqing experience",
        "price_range": "¥60-80/人",
        "tips": ["毛肚必点", "配唯怡豆奶解辣", "排队严重，建议17:30前到"],
        "track": "budget",
        "rating": 4.6,
    },
    {
        "id": "cq_peijie_hotpot",
        "name_zh": "佩姐老火锅",
        "name_en": "Peijie Old Hotpot",
        "city": "chongqing",
        "type": "restaurant",
        "lat": 29.5606, "lng": 106.5744,
        "tags": ["火锅", "老字号", "辣"],
        "description_zh": "重庆排队王，牛油锅底厚重，本地人认证",
        "description_en": "Chongqing's queue king — heavy beef tallow broth, local-approved",
        "price_range": "¥80-100/人",
        "tips": ["下午4点开始排队", "九宫格全红汤是灵魂"],
        "track": "both",
        "rating": 4.7,
    },
    {
        "id": "cq_haoyoulai_noodles",
        "name_zh": "好又来酸辣粉",
        "name_en": "Haoyoulai Hot & Sour Noodles",
        "city": "chongqing",
        "type": "restaurant",
        "lat": 29.5553, "lng": 106.5683,
        "tags": ["小吃", "酸辣粉", "街边", "必吃"],
        "description_zh": "解放碑八一路的传奇酸辣粉，人均15元",
        "description_en": "Legendary hot & sour rice noodles at Bayi Road, ¥15/person",
        "price_range": "¥12-18/碗",
        "tips": ["买完站路边吃才是正确姿势", "加一勺醋更地道"],
        "track": "budget",
        "rating": 4.6,
    },
    {
        "id": "cq_small_noodles",
        "name_zh": "花市豌杂面",
        "name_en": "Huashi Pea Noodles",
        "city": "chongqing",
        "type": "restaurant",
        "lat": 29.5569, "lng": 106.5689,
        "tags": ["小面", "早餐", "老字号", "必吃"],
        "description_zh": "重庆小面界的天花板，豌豆杂酱面是招牌",
        "description_en": "The pinnacle of Chongqing noodles — pea & minced pork is the signature",
        "price_range": "¥15-20/碗",
        "tips": ["14:00前要到，晚了卖完", "二两就够了别点多"],
        "track": "budget",
        "rating": 4.7,
    },
    {
        "id": "cq_chenxiang",
        "name_zh": "尘香新派川菜",
        "name_en": "Chenxiang Modern Sichuan",
        "city": "chongqing",
        "type": "restaurant",
        "lat": 29.5839, "lng": 106.5461,
        "tags": ["川菜", "高档", "黑珍珠"],
        "description_zh": "黑珍珠一钻新派川菜，精致不失传统",
        "description_en": "Black Pearl one-diamond modern Sichuan cuisine — refined yet traditional",
        "price_range": "¥200-400/人",
        "tips": ["提前3天订位", "推荐：宫保虾球、樟茶鸭"],
        "track": "premium",
        "rating": 4.8,
    },
    {
        "id": "cq_wanwan_lamb",
        "name_zh": "武隆碗碗羊肉",
        "name_en": "Wulong Bowl Lamb",
        "city": "chongqing",
        "type": "restaurant",
        "lat": 29.3256, "lng": 107.7961,
        "tags": ["羊肉", "武隆特色", "暖身"],
        "description_zh": "武隆当地特色，小碗蒸羊肉配薄荷，汤鲜肉嫩",
        "description_en": "Wulong specialty — steamed lamb in small bowls with mint, tender and warming",
        "price_range": "¥30-50/人",
        "tips": ["天生三桥景区附近就有", "冬季吃正好暖身"],
        "track": "budget",
        "rating": 4.4,
    },
    {
        "id": "cq_fengjie_chicken",
        "name_zh": "奉节盬子鸡",
        "name_en": "Fengjie Claypot Chicken",
        "city": "chongqing",
        "type": "restaurant",
        "lat": 31.0183, "lng": 109.4639,
        "tags": ["土鸡", "奉节特色", "非遗美食"],
        "description_zh": "本地非遗美食，陶罐慢蒸土鸡，汤浓肉烂",
        "description_en": "Local intangible heritage dish — claypot slow-steamed free-range chicken",
        "price_range": "¥80-120/份",
        "tips": ["适合2-3人分享", "白帝城附近可找到"],
        "track": "both",
        "rating": 4.5,
    },
    {
        "id": "cq_wushan_fish",
        "name_zh": "巫山烤鱼",
        "name_en": "Wushan Grilled Fish",
        "city": "chongqing",
        "type": "restaurant",
        "lat": 31.0778, "lng": 109.8761,
        "tags": ["烤鱼", "长江鱼", "巫山特色"],
        "description_zh": "长江边的烤鱼，和主城烤鱼不是一个物种",
        "description_en": "Riverside grilled fish — different species from city grilled fish",
        "price_range": "¥60-100/条",
        "tips": ["点长江鮰鱼或江团", "配冰啤酒完美"],
        "track": "both",
        "rating": 4.6,
    },
    {
        "id": "cq_guanyingqiao_street",
        "name_zh": "观音桥好吃街",
        "name_en": "Guanyinqiao Food Street",
        "city": "chongqing",
        "type": "restaurant",
        "lat": 29.5769, "lng": 106.5303,
        "tags": ["小吃街", "平价", "本地人"],
        "description_zh": "重庆最接地气的美食街：烤脑花、冰粉凉虾、山城汤圆",
        "description_en": "Most down-to-earth food street: grilled brain, iced jelly, local desserts",
        "price_range": "¥20-50/人",
        "tips": ["下午开始热闹，一直到深夜", "每家少买点多尝几家"],
        "track": "budget",
        "rating": 4.4,
    },

    # ══ Extended Hotels ══
    {
        "id": "cq_nanshan_inn",
        "name_zh": "南山山觉行舍民宿",
        "name_en": "Nanshan Mountain Retreat",
        "city": "chongqing",
        "type": "hotel",
        "lat": 29.5183, "lng": 106.6167,
        "tags": ["民宿", "山景", "避暑", "安静"],
        "description_zh": "南山山顶民宿，被鸟叫醒，阳台看日出云海",
        "description_en": "Hilltop guesthouse — wake up to birdsong, sunrise and sea of clouds from your balcony",
        "price_range": "¥400-800/晚",
        "tips": ["比市区凉快5°C", "需提前一周订"],
        "track": "both",
        "rating": 4.6,
    },
    {
        "id": "cq_ji_hotel",
        "name_zh": "全季酒店（观音桥）",
        "name_en": "JI Hotel Guanyinqiao",
        "city": "chongqing",
        "type": "hotel",
        "lat": 29.5750, "lng": 106.5283,
        "tags": ["连锁", "干净", "性价比"],
        "description_zh": "观音桥商圈便捷酒店，干净标准不踩雷",
        "description_en": "Reliable chain hotel in Guanyinqiao — clean, standard, no surprises",
        "price_range": "¥250-400/晚",
        "tips": ["楼下就是轻轨3号线", "周边吃的多，步行可达好吃街"],
        "track": "budget",
        "rating": 4.3,
    },
    {
        "id": "cq_radisson",
        "name_zh": "南滨路丽笙世嘉酒店",
        "name_en": "Radisson Blu Nanbin Road",
        "city": "chongqing",
        "type": "hotel",
        "lat": 29.5494, "lng": 106.5853,
        "tags": ["江景", "南滨路", "看夜景"],
        "description_zh": "南滨路一线江景，正对渝中半岛夜景",
        "description_en": "Premium riverfront hotel on Nanbin Road, directly facing Yuzhong Peninsula night view",
        "price_range": "¥600-1200/晚",
        "tips": ["预订江景房型", "行政酒廊可看两江交汇"],
        "track": "premium",
        "rating": 4.5,
    },
    {
        "id": "cq_wulong_hotel",
        "name_zh": "仙女山假日酒店",
        "name_en": "Fairy Mountain Holiday Hotel",
        "city": "chongqing",
        "type": "hotel",
        "lat": 29.3667, "lng": 107.7667,
        "tags": ["武隆", "度假", "草原"],
        "description_zh": "仙女山镇度假酒店，离天生三桥20分钟车程，含早餐",
        "description_en": "Resort hotel in Fairy Mountain town, 20min drive to Three Natural Bridges, breakfast included",
        "price_range": "¥400-700/晚",
        "tips": ["武隆过夜首选", "旺季提前两周订"],
        "track": "both",
        "rating": 4.3,
    },

    # ══ Extended Experiences ══
    {
        "id": "cq_sichuan_opera",
        "name_zh": "重庆川剧院 · 变脸演出",
        "name_en": "Chongqing Sichuan Opera — Face Changing",
        "city": "chongqing",
        "type": "experience",
        "lat": 29.5606, "lng": 106.5833,
        "tags": ["川剧", "变脸", "非遗", "文化"],
        "description_zh": "300年川剧绝活，一秒换脸的神奇魔法",
        "description_en": "300-year-old opera magic — faces change in a split second",
        "price_range": "¥100-300/人",
        "opening_hours": "每晚19:30（约1.5小时）",
        "tips": ["湖广会馆和重庆川剧院都有演出", "部分剧场提供后台探秘"],
        "track": "premium",
        "rating": 4.8,
    },
    {
        "id": "cq_hotpot_diy",
        "name_zh": "火锅底料工坊体验",
        "name_en": "Hotpot Base DIY Workshop",
        "city": "chongqing",
        "type": "experience",
        "lat": 29.5633, "lng": 106.5722,
        "tags": ["火锅", "DIY", "伴手礼"],
        "description_zh": "学炒火锅底料：牛油、辣椒、花椒的黄金比例，炒完带走",
        "description_en": "Learn to fry hotpot base — master the ratio of beef tallow, chili, and Sichuan pepper. Take yours home.",
        "price_range": "¥150-200/人",
        "tips": ["成品密封可带上飞机", "需提前一天预约"],
        "track": "both",
        "rating": 4.6,
    },
    {
        "id": "cq_xiabu_workshop",
        "name_zh": "荣昌夏布手工艺体验",
        "name_en": "Rongchang Xiabu Weaving",
        "city": "chongqing",
        "type": "experience",
        "lat": 29.4106, "lng": 105.5944,
        "tags": ["手工艺", "非遗", "夏布", "织布"],
        "description_zh": "千年夏布织造工艺，亲手织一小块带回家",
        "description_en": "Weave a piece of 1000-year-old ramie fabric yourself — and take it home",
        "price_range": "¥80-120/人",
        "tips": ["主城有体验馆", "成品可作围巾或茶巾"],
        "track": "both",
        "rating": 4.4,
    },
    {
        "id": "cq_tongliang_dragon",
        "name_zh": "铜梁火龙表演",
        "name_en": "Tongliang Fire Dragon Dance",
        "city": "chongqing",
        "type": "experience",
        "lat": 29.8431, "lng": 106.0631,
        "tags": ["非遗", "龙舞", "节日", "壮观"],
        "description_zh": "联合国人类非遗，50米火龙在漫天火花中狂舞",
        "description_en": "UNESCO Intangible Heritage — 50m dragon dancing in a storm of sparks",
        "price_range": "免费观赏（节庆活动）",
        "opening_hours": "农历正月十五前后",
        "tips": ["仅在春节期间有", "铜梁距重庆主城约1小时车程"],
        "track": "both",
        "rating": 4.7,
    },
    {
        "id": "cq_night_hike",
        "name_zh": "戴家巷悬崖步道夜游",
        "name_en": "Daijia Lane Cliff Walk (Night)",
        "city": "chongqing",
        "type": "experience",
        "lat": 29.5639, "lng": 106.5819,
        "tags": ["夜景", "徒步", "小众", "拍照"],
        "description_zh": "洪崖洞旁边人少景美的悬崖步道，纵向看洪崖洞+嘉陵江",
        "description_en": "Quiet cliff walk beside Hongya Cave — vertical angle of Hongya + Jialing River",
        "price_range": "免费",
        "tips": ["19:00后亮灯去最美", "比千厮门大桥视角更独特"],
        "track": "both",
        "rating": 4.4,
    },
    {
        "id": "cq_ciqikou_tea",
        "name_zh": "磁器口老茶馆",
        "name_en": "Ciqikou Old Teahouse",
        "city": "chongqing",
        "type": "experience",
        "lat": 29.5797, "lng": 106.4478,
        "tags": ["茶馆", "古镇", "慢生活"],
        "description_zh": "磁器口小巷里开了40年的茶馆，80岁老茶娘用盖碗泡茶",
        "description_en": "40-year-old teahouse in Ciqikou alley — 80-year-old lady pours tea in covered bowls",
        "price_range": "¥8-15/杯",
        "tips": ["早上10点前到人少", "岔进小巷子才能找到"],
        "track": "budget",
        "rating": 4.5,
    },

    # ══ Transport / Practical POIs ══
    {
        "id": "cq_airport",
        "name_zh": "重庆江北国际机场",
        "name_en": "Chongqing Jiangbei Airport (CKG)",
        "city": "chongqing",
        "type": "transport",
        "lat": 29.7194, "lng": 106.6417,
        "tags": ["机场", "交通枢纽"],
        "description_zh": "重庆主要国际机场，轻轨3号线/10号线直达市区",
        "description_en": "Main international airport, Metro Line 3/10 to city center",
        "price_range": "",
        "tips": ["到解放碑约40分钟车程", "轻轨10号线最快"],
        "track": "both",
        "rating": 4.2,
    },
    {
        "id": "cq_train_north",
        "name_zh": "重庆北站",
        "name_en": "Chongqing North Railway Station",
        "city": "chongqing",
        "type": "transport",
        "lat": 29.6106, "lng": 106.5494,
        "tags": ["火车站", "交通枢纽"],
        "description_zh": "主要高铁站，通往武隆/成都/西安方向",
        "description_en": "Main high-speed rail station, connections to Wulong/Chengdu/Xi'an",
        "price_range": "",
        "tips": ["北广场和南广场相通但很远，看清车票", "轻轨环线和3号线直达"],
        "track": "both",
        "rating": 4.0,
    },
    {
        "id": "cq_train_west",
        "name_zh": "重庆西站",
        "name_en": "Chongqing West Railway Station",
        "city": "chongqing",
        "type": "transport",
        "lat": 29.4978, "lng": 106.4558,
        "tags": ["火车站", "交通枢纽"],
        "description_zh": "通往大足石刻/云南方向的高铁站",
        "description_en": "High-speed rail station to Dazu Rock Carvings / Yunnan direction",
        "price_range": "",
        "tips": ["到大足南约30分钟高铁", "轻轨环线直达"],
        "track": "both",
        "rating": 3.8,
    },
    {
        "id": "cq_metro_line2",
        "name_zh": "轻轨2号线（沿江线）",
        "name_en": "Metro Line 2 (Riverside Line)",
        "city": "chongqing",
        "type": "transport",
        "lat": 29.5528, "lng": 106.5369,
        "tags": ["轻轨", "观光", "沿江"],
        "description_zh": "重庆最美轻轨线，沿嘉陵江跑，途经李子坝穿楼站",
        "description_en": "Most scenic metro line, runs along Jialing River, passes through Liziba building",
        "price_range": "¥2-7/程",
        "tips": ["较场口→李子坝段最美", "右侧靠窗座位拍照最佳"],
        "track": "both",
        "rating": 4.8,
    },
    {
        "id": "cq_kailu_elevator",
        "name_zh": "凯旋路电梯",
        "name_en": "Kailu Road Elevator",
        "city": "chongqing",
        "type": "transport",
        "lat": 29.5550, "lng": 106.5736,
        "tags": ["电梯", "公共交通", "奇观"],
        "description_zh": "中国第一部城市客运电梯，1元从下半城到上半城",
        "description_en": "China's first urban passenger elevator — ¥1 to go from Lower to Upper City",
        "price_range": "¥1/次",
        "tips": ["较场口附近", "体验重庆8D交通的入门级项目"],
        "track": "budget",
        "rating": 4.3,
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
