"""Tests: Health & POI APIs"""
import pytest


@pytest.mark.asyncio
async def test_health(client):
    resp = await client.get("/api/health")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "ok"
    assert data["city"] == "chongqing"


@pytest.mark.asyncio
async def test_list_pois(client):
    resp = await client.get("/api/planner/pois")
    assert resp.status_code == 200
    data = resp.json()
    assert "results" in data
    assert data["count"] >= 10


@pytest.mark.asyncio
async def test_list_pois_filter_by_track(client):
    resp = await client.get("/api/planner/pois?track=premium")
    assert resp.status_code == 200
    results = resp.json()["results"]
    tracks = {p.get("track", "both") for p in results}
    assert tracks.issubset({"premium", "both"})


@pytest.mark.asyncio
async def test_list_pois_filter_by_type(client):
    resp = await client.get("/api/planner/pois?type=attraction")
    assert resp.status_code == 200
    results = resp.json()["results"]
    for p in results:
        assert p["type"] == "attraction"


@pytest.mark.asyncio
async def test_poi_detail_exists(client):
    resp = await client.get("/api/planner/pois/cq_hongya_cave")
    assert resp.status_code == 200
    assert resp.json()["name_zh"] == "洪崖洞"


@pytest.mark.asyncio
async def test_poi_detail_not_found(client):
    resp = await client.get("/api/planner/pois/nonexistent")
    assert resp.status_code == 404
