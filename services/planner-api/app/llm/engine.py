"""LLM Service — Function Calling + SSE Streaming

Uses OpenAI-compatible API (DeepSeek / GPT-4o).
"""

from __future__ import annotations

import json
import asyncio
from typing import AsyncGenerator

import httpx

from app.core.config import settings
from app.models.schemas import ChatMessage

# ═══════════════════════════════════════════════════════
# Function Definitions (7 tools)
# ═══════════════════════════════════════════════════════

FUNCTIONS = [
    {
        "name": "search_poi",
        "description": "搜索重庆的景点、餐厅、体验项目。输入关键词或类型，返回POI列表。",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "搜索关键词，如'火锅''夜景''古镇'"},
                "poi_type": {
                    "type": "string",
                    "enum": ["attraction", "restaurant", "hotel", "experience", "transport"],
                    "description": "POI类型筛选"
                },
                "track": {
                    "type": "string",
                    "enum": ["premium", "budget", "both"],
                    "description": "价格档次：premium高端 / budget经济"
                },
                "limit": {"type": "integer", "default": 5},
            },
            "required": ["query"],
        },
    },
    {
        "name": "search_hotel",
        "description": "搜索重庆酒店，按区域和价格筛选。",
        "parameters": {
            "type": "object",
            "properties": {
                "area": {"type": "string", "description": "区域，如'解放碑''南滨路''观音桥'"},
                "track": {
                    "type": "string",
                    "enum": ["premium", "budget"],
                    "description": "高端酒店 or 经济民宿/青旅"
                },
                "limit": {"type": "integer", "default": 3},
            },
            "required": ["track"],
        },
    },
    {
        "name": "get_transport",
        "description": "查询重庆市内交通方式、耗时和费用。",
        "parameters": {
            "type": "object",
            "properties": {
                "origin": {"type": "string", "description": "出发地名称"},
                "destination": {"type": "string", "description": "目的地名称"},
                "mode": {
                    "type": "string",
                    "enum": ["metro", "bus", "taxi", "walk", "cableway"],
                    "description": "交通方式"
                },
            },
            "required": ["origin", "destination"],
        },
    },
    {
        "name": "calculate_price",
        "description": "估算一段行程的费用。输入每日计划的项目，返回费用预估。",
        "parameters": {
            "type": "object",
            "properties": {
                "items": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "poi_name": {"type": "string"},
                            "poi_type": {"type": "string"},
                        },
                    },
                    "description": "行程项目列表"
                },
                "track": {
                    "type": "string",
                    "enum": ["premium", "budget"],
                },
                "days": {"type": "integer", "default": 3},
            },
            "required": ["items", "track"],
        },
    },
    {
        "name": "generate_itinerary",
        "description": "根据用户偏好和已查询的POI数据，生成完整的重庆行程计划（Premium或Budget）。输出结构化JSON。",
        "parameters": {
            "type": "object",
            "properties": {
                "days": {"type": "integer", "description": "行程天数"},
                "track": {
                    "type": "string",
                    "enum": ["premium", "budget"],
                    "description": "行程档次"
                },
                "preferences": {
                    "type": "string",
                    "description": "用户偏好摘要，如'喜欢美食和夜景，带老人出行'"
                },
                "selected_pois": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "选中的POI名称列表"
                },
            },
            "required": ["days", "track", "preferences"],
        },
    },
    {
        "name": "get_weather_tip",
        "description": "获取重庆近期天气和出行建议。",
        "parameters": {
            "type": "object",
            "properties": {
                "month": {"type": "string", "description": "出行月份，如'6月''10月'"},
            },
            "required": ["month"],
        },
    },
    {
        "name": "translate_tip",
        "description": "将中文旅行贴士翻译为英文，并做跨文化润色。",
        "parameters": {
            "type": "object",
            "properties": {
                "text_zh": {"type": "string", "description": "需要翻译的中文贴士"},
            },
            "required": ["text_zh"],
        },
    },
]

SYSTEM_PROMPT = """You are a Chongqing Local Travel Planner — a native who knows every corner of the city, from Michelin-starred restaurants to hidden alleyway noodles.

Your personality: warm, knowledgeable, slightly humorous. You call Chongqing "the 8D magical city" (8D魔幻城市).

## Your Job
1. Understand the traveler's needs through conversation — budget, interests, pace, special requirements
2. Use tools to search REAL POIs (attractions, restaurants, hotels) — never make them up
3. When you have enough information, generate a complete {days}-day itinerary in TWO versions:
   - Premium (高端品质): Luxury hotels, private car, fine dining, exclusive experiences
   - Budget (高性价比): Local gems, public transit, street food, free attractions
4. Output itinerary in structured JSON format

## Important Rules
- ALWAYS call search_poi / search_hotel before recommending anything
- NEVER fabricate POI names or prices
- Speak in Chinese to Chinese-speaking users, English to English-speaking users
- When generating itinerary, output as a valid JSON array of DayPlan objects
- For Chongqing specifically: mention the city's unique features — mountain city topography, hotpot culture, river night views, light rail through buildings (李子坝)

## Current City: Chongqing (重庆)
"""


# ═══════════════════════════════════════════════════════
# Function Executors
# ═══════════════════════════════════════════════════════

async def execute_function(name: str, args: dict) -> dict:
    """Execute a function call and return the result."""
    from app.services.poi_store import POIStore

    store = POIStore()

    if name == "search_poi":
        return await store.search_poi(
            query=args.get("query", ""),
            poi_type=args.get("poi_type"),
            track=args.get("track", "both"),
            limit=args.get("limit", 5),
        )
    elif name == "search_hotel":
        return await store.search_hotel(
            area=args.get("area"),
            track=args.get("track", "budget"),
            limit=args.get("limit", 3),
        )
    elif name == "get_transport":
        return await store.get_transport(
            origin=args.get("origin", ""),
            destination=args.get("destination", ""),
            mode=args.get("mode", "metro"),
        )
    elif name == "calculate_price":
        return await store.calculate_price(
            items=args.get("items", []),
            track=args.get("track", "budget"),
            days=args.get("days", 3),
        )
    elif name == "generate_itinerary":
        return await store.generate_itinerary_struct(
            days=args.get("days", 3),
            track=args.get("track", "budget"),
            preferences=args.get("preferences", ""),
            selected_pois=args.get("selected_pois", []),
        )
    elif name == "get_weather_tip":
        return {
            "month": args.get("month", "6月"),
            "avg_temp": "25-33°C",
            "weather": "hot and humid, occasional thunderstorms",
            "tips": [
                "带雨伞，重庆夏天阵雨频繁",
                "穿轻薄透气的衣服",
                "防晒霜必备",
                "上午11点前或下午4点后户外活动较舒适",
            ],
            "tips_en": [
                "Bring an umbrella — summer showers are frequent in Chongqing",
                "Wear light, breathable clothing",
                "Sunscreen is a must",
                "Best to do outdoor activities before 11am or after 4pm",
            ],
        }
    elif name == "translate_tip":
        text = args.get("text_zh", "")
        return {
            "original": text,
            "translated": f"[EN] {text} (translated & culturally adapted)",
            "note": "MVP: placeholder translation — connect LLM for real translation",
        }

    return {"error": f"Unknown function: {name}"}


# ═══════════════════════════════════════════════════════
# LLM Chat with Tool Calling
# ═══════════════════════════════════════════════════════

async def chat_with_tools(
    messages: list[ChatMessage],
    track: str | None = None,
) -> AsyncGenerator[dict, None]:
    """
    SSE streaming chat with function calling.
    Yields SSE events: message, function_call, function_result, itinerary, done, error.
    """
    client = httpx.AsyncClient(timeout=60.0)

    # Build system message
    sys_content = SYSTEM_PROMPT.format(days="3")
    if track:
        sys_content += f"\n\nThe user has pre-selected the {track} track. Focus on this track."

    api_messages = [
        {"role": "system", "content": sys_content},
    ]
    for m in messages:
        api_messages.append({"role": m.role, "content": m.content})

    try:
        # Step 1: First LLM call with tools
        response = await client.post(
            f"{settings.llm_base_url}/chat/completions",
            headers={
                "Authorization": f"Bearer {settings.llm_api_key}",
                "Content-Type": "application/json",
            },
            json={
                "model": settings.llm_model,
                "messages": api_messages,
                "tools": [
                    {"type": "function", "function": f} for f in FUNCTIONS
                ],
                "tool_choice": "auto",
                "temperature": 0.7,
                "stream": True,
            },
        )
        response.raise_for_status()

        # Step 2: Stream response, collect tool calls
        collected_content = ""
        tool_calls: dict[int, dict] = {}  # index -> {id, name, args}

        async for line in response.aiter_lines():
            if not line.startswith("data: "):
                continue
            data_str = line[6:]
            if data_str == "[DONE]":
                break

            try:
                chunk = json.loads(data_str)
                choice = chunk["choices"][0]
                delta = choice.get("delta", {})

                # Text content
                if delta.get("content"):
                    collected_content += delta["content"]
                    yield {
                        "event": "message",
                        "data": {"content": delta["content"]},
                    }

                # Tool calls
                if delta.get("tool_calls"):
                    for tc in delta["tool_calls"]:
                        idx = tc.get("index", 0)
                        if idx not in tool_calls:
                            tool_calls[idx] = {
                                "id": tc.get("id", ""),
                                "name": "",
                                "arguments": "",
                            }
                        if tc.get("id"):
                            tool_calls[idx]["id"] = tc["id"]
                        if tc.get("function", {}).get("name"):
                            tool_calls[idx]["name"] = tc["function"]["name"]
                            yield {
                                "event": "function_call",
                                "data": {
                                    "name": tc["function"]["name"],
                                    "status": "calling",
                                },
                            }
                        if tc.get("function", {}).get("arguments"):
                            tool_calls[idx]["arguments"] += tc["function"]["arguments"]

                # Finish reason
                if choice.get("finish_reason"):
                    pass

            except json.JSONDecodeError:
                continue

        # Step 3: Execute tool calls and feed results back
        if tool_calls:
            # Add assistant message with tool calls
            assistant_tool_calls = []
            for idx in sorted(tool_calls.keys()):
                tc = tool_calls[idx]
                try:
                    args = json.loads(tc["arguments"])
                except json.JSONDecodeError:
                    args = {}
                assistant_tool_calls.append({
                    "id": tc["id"],
                    "type": "function",
                    "function": {
                        "name": tc["name"],
                        "arguments": tc["arguments"],
                    },
                })

            api_messages.append({
                "role": "assistant",
                "content": collected_content or None,
                "tool_calls": assistant_tool_calls,
            })

            # Execute each function
            for idx in sorted(tool_calls.keys()):
                tc = tool_calls[idx]
                try:
                    args = json.loads(tc["arguments"])
                except json.JSONDecodeError:
                    args = {}

                result = await execute_function(tc["name"], args)
                yield {
                    "event": "function_result",
                    "data": {
                        "name": tc["name"],
                        "result": result,
                    },
                }

                api_messages.append({
                    "role": "tool",
                    "tool_call_id": tc["id"],
                    "content": json.dumps(result, ensure_ascii=False),
                })

            # Step 4: Final LLM call to generate response with function results
            final_response = await client.post(
                f"{settings.llm_base_url}/chat/completions",
                headers={
                    "Authorization": f"Bearer {settings.llm_api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": settings.llm_model,
                    "messages": api_messages,
                    "temperature": 0.7,
                    "stream": True,
                },
            )
            final_response.raise_for_status()

            async for line in final_response.aiter_lines():
                if not line.startswith("data: "):
                    continue
                data_str = line[6:]
                if data_str == "[DONE]":
                    break
                try:
                    chunk = json.loads(data_str)
                    delta = chunk["choices"][0].get("delta", {})
                    if delta.get("content"):
                        yield {
                            "event": "message",
                            "data": {"content": delta["content"]},
                        }
                except json.JSONDecodeError:
                    continue

        yield {"event": "done", "data": {"status": "complete"}}

    except httpx.HTTPError as e:
        yield {
            "event": "error",
            "data": {"message": f"LLM API error: {str(e)}"},
        }
    finally:
        await client.aclose()
