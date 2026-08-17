import pytest
from app.core.prompt import get_system_prompt
from app.core.agent import AgentOrchestrator
from app.services.memory_service import MemoryService
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_system_prompt_not_empty():
    prompt = get_system_prompt()
    assert prompt is not None
    assert len(prompt) > 0

def test_system_prompt_voice_compatibility():
    prompt = get_system_prompt()
    # Confirm no markdown asterisks or hash characters
    assert "*" not in prompt, "Asterisks * found in prompt. This is incompatible with voice output."
    assert "#" not in prompt, "Hash symbol # found in prompt. This is incompatible with voice output."
    
    # Ensure no lines represent markdown lists
    for line in prompt.splitlines():
        trimmed = line.strip()
        assert not trimmed.startswith("- "), f"Dash bullet point found: {trimmed}."
        assert not trimmed.startswith("* "), f"Asterisk bullet point found: {trimmed}."
        assert not trimmed.startswith("1. "), f"Numbered list item found: {trimmed}."

@pytest.mark.asyncio
async def test_agent_multi_turn_and_hinglish():
    orchestrator = AgentOrchestrator()
    session_id = "test-multi-turn-session"
    
    # Turn 1: English hello
    res1 = await orchestrator.process_chat(session_id, "Hello, is this Priya?")
    assert res1["response"] is not None
    assert not any(char in res1["response"] for char in ["*", "#"])
    
    # Turn 2: Hinglish pricing query
    res2 = await orchestrator.process_chat(session_id, "2 BHK ka price kya hai?")
    assert res2["response"] is not None
    # Hinglish response should mention start price
    assert "1.35 Crore" in res2["response"]

@pytest.mark.asyncio
async def test_agent_dnd_opt_out():
    orchestrator = AgentOrchestrator()
    session_id = "test-dnd-session"
    
    # Trigger DND / Opt-out
    res1 = await orchestrator.process_chat(session_id, "Please opt me out / unsubscribe")
    assert "records" in res1["response"] or "messages" in res1["response"]
    
    # Check that opt-out is recorded
    memory_service = MemoryService()
    assert memory_service.is_opted_out(session_id) is True
    
    # Send another message, expect automatic DND response
    res2 = await orchestrator.process_chat(session_id, "Are you there?")
    assert "not receive further messages" in res2["response"]

def test_api_chat_endpoint():
    response = client.post("/api/chat", json={"session_id": "test-api-session", "message": "Hi"})
    assert response.status_code == 200
    data = response.json()
    assert "response" in data
    assert data["session_id"] == "test-api-session"
    assert data["opt_out"] is False
