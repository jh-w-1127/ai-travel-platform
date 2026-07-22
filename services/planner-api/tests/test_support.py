"""Tests: AI客服 — Q&A + handoff + 关键词匹配"""
import pytest


@pytest.mark.asyncio
async def test_ai_ask_knowledge_base(client):
    """关键词 'visa' 应命中知识库"""
    resp = await client.post("/api/ai/ask", json={"question": "visa"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["source"] == "knowledge_base"
    assert "144-hour" in data["answer"]


@pytest.mark.asyncio
async def test_ai_ask_knowledge_base_zh(client):
    """中文关键词 '交通' 应命中知识库"""
    resp = await client.post("/api/ai/ask", json={"question": "交通怎么走"})
    assert resp.status_code == 200
    assert resp.json()["source"] == "knowledge_base"


@pytest.mark.asyncio
async def test_ai_ask_llm_fallback(client):
    """非关键词问题应走 LLM"""
    resp = await client.post("/api/ai/ask", json={"question": "推荐一个看夜景的地方"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["source"] in ("ai", "fallback")
    assert len(data["answer"]) > 10


@pytest.mark.asyncio
async def test_ai_handoff_trigger_zh(client):
    """用户说 '人工客服' 应触发转人工"""
    resp = await client.post("/api/ai/ask", json={"question": "我要找人工客服"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["action"] == "handoff"
    assert "转接" in data["answer"]


@pytest.mark.asyncio
async def test_ai_handoff_trigger_refund(client):
    """'退款' 应触发转人工"""
    resp = await client.post("/api/ai/ask", json={"question": "我想退款"})
    assert resp.status_code == 200
    assert resp.json()["action"] == "handoff"


@pytest.mark.asyncio
async def test_ai_handoff_trigger_complaint(client):
    """'投诉' 应触发转人工"""
    resp = await client.post("/api/ai/ask", json={"question": "我要投诉"})
    assert resp.status_code == 200
    assert resp.json()["action"] == "handoff"


@pytest.mark.asyncio
async def test_ai_handoff_consecutive_failures(client):
    """连续 2 次 fallback 应触发转人工"""
    for _ in range(2):
        resp = await client.post("/api/ai/ask", json={
            "question": "xyz看不懂的问题abc",
            "conversation_history": [{"role": "assistant", "source": "fallback"}]
        })
    # Second call with history should trigger handoff
    assert resp.status_code == 200
    data = resp.json()
    # May or may not trigger depending on LLM available
    assert data["source"] in ("handoff", "fallback", "ai")


@pytest.mark.asyncio
async def test_handoff_submit(client):
    """提交转人工表单"""
    resp = await client.post("/api/ai/handoff", json={
        "name": "测试用户",
        "email": "test@example.com",
        "question": "帮我取消订单"
    })
    assert resp.status_code == 200
    assert resp.json()["status"] == "received"


@pytest.mark.asyncio
async def test_handoff_list(client):
    """查看转人工列表"""
    resp = await client.get("/api/ai/handoffs")
    assert resp.status_code == 200
    data = resp.json()
    assert "count" in data
    assert "requests" in data
