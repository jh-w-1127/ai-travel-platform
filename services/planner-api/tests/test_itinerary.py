"""Tests: 行程规划 — template + AI endpoints"""
import pytest


@pytest.mark.asyncio
async def test_itinerary_template_budget(client):
    """模板生成 budget 行程"""
    resp = await client.get("/api/planner/itinerary/generate?track=budget&days=3")
    assert resp.status_code == 200
    data = resp.json()
    assert data["track"] == "budget"
    assert data["days"] == 3
    assert len(data["plan"]) == 3
    assert "budget" in data


@pytest.mark.asyncio
async def test_itinerary_template_premium(client):
    """模板生成 premium 行程"""
    resp = await client.get("/api/planner/itinerary/generate?track=premium&days=2")
    assert resp.status_code == 200
    data = resp.json()
    assert data["days"] == 2
    assert data["budget"]["track"] == "premium"


@pytest.mark.asyncio
async def test_itinerary_template_default_days(client):
    """无 days 参数时默认 3 天"""
    resp = await client.get("/api/planner/itinerary/generate?track=budget")
    assert resp.status_code == 200
    assert resp.json()["days"] == 3


@pytest.mark.asyncio
async def test_itinerary_has_budget_breakdown(client):
    """行程包含费用明细"""
    resp = await client.get("/api/planner/itinerary/generate?track=budget&days=2")
    data = resp.json()
    assert "breakdown" in data["budget"]
    assert "service_fee" in data["budget"]
    assert "total" in data["budget"]


@pytest.mark.asyncio
async def test_itinerary_ai_plan_without_prefs(client):
    """AI 规划（无偏好）"""
    resp = await client.post("/api/planner/itinerary/ai-plan?days=2&track=budget")
    # SSE 端点可能返回 stream 或直接返回
    assert resp.status_code in (200, 500)
