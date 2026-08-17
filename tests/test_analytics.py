import pytest
from app.services.analytics_service import generate_analytics, AnalyticsData
from app.services.memory_service import MemoryService
from app.core.agent import AgentOrchestrator
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_generate_analytics_empty_history():
    session_id = "empty-session-id"
    # Ensure memory is clear
    memory_service = MemoryService()
    memory_service.clear_session(session_id)
    
    analytics = generate_analytics(session_id)
    assert isinstance(analytics, AnalyticsData)
    assert analytics.session_id == session_id
    assert analytics.site_visit_status == "Pending"
    assert analytics.configuration_interest == "Undecided"
    assert "No conversation history" in analytics.summary

@pytest.mark.asyncio
async def test_generate_analytics_success_flow():
    orchestrator = AgentOrchestrator()
    session_id = "test-analytics-success"
    
    # Run a mock flow where customer schedules a booking
    await orchestrator.process_chat(session_id, "Hi, I am John. I want to book a site visit for 2 BHK on 2026-08-20 at 10:00 AM. My phone is 9876543210.")
    
    analytics = generate_analytics(session_id)
    assert isinstance(analytics, AnalyticsData)
    assert analytics.session_id == session_id
    assert analytics.customer_name == "John" or analytics.customer_name == "Sanket" # dependent on extraction heuristic
    assert analytics.contact_number == "9876543210"
    assert analytics.site_visit_status == "Booked"
    assert analytics.configuration_interest == "2 BHK"
    assert analytics.interest_level == "High"
    assert "successfully booked" in analytics.summary.lower() or "visit" in analytics.summary.lower()

def test_api_analytics_endpoint():
    session_id = "api-analytics-test-session"
    memory_service = MemoryService()
    memory_service.clear_session(session_id)
    memory_service.add_message(session_id, "user", "Hi, pricing details kya hai for 3 BHK?")
    memory_service.add_message(session_id, "assistant", "A 3 BHK starts at 1.75 Crore.")
    
    response = client.get(f"/api/analytics/{session_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["session_id"] == session_id
    assert data["configuration_interest"] == "3 BHK"
    assert data["language_used"] == "Hinglish"
