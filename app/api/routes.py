from fastapi import APIRouter, HTTPException
from app.api.schemas import ChatRequest, ChatResponse, BookingRequest, BookingResponse, ResetRequest
from app.core.agent import AgentOrchestrator
from app.services.booking_service import book_site_visit
from app.services.memory_service import MemoryService
from app.services.analytics_service import generate_analytics, AnalyticsData

router = APIRouter()

# Global instances of orchestrator and memory service
agent_orchestrator = AgentOrchestrator()
memory_service = MemoryService()

@router.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    """
    POST /api/chat
    Processes conversation turn, updates session history, runs tool calls, and returns agent response.
    """
    res = await agent_orchestrator.process_chat(
        session_id=request.session_id,
        user_message=request.message
    )
    
    # Check if session has been marked opted out
    opt_out_status = memory_service.is_opted_out(request.session_id)
    
    return ChatResponse(
        session_id=request.session_id,
        response=res.get("response", ""),
        booking_details=res.get("booking_details"),
        opt_out=opt_out_status
    )

@router.post("/booking", response_model=BookingResponse)
async def booking_endpoint(request: BookingRequest):
    """
    POST /api/booking
    Direct endpoint to schedule/mock a site visit booking.
    """
    res = book_site_visit(
        customer_name=request.customer_name,
        phone_number=request.phone_number,
        preferred_date=request.preferred_date,
        preferred_time=request.preferred_time,
        configuration_interest=request.configuration_interest or "Unspecified"
    )
    
    if not res.get("success"):
        raise HTTPException(status_code=400, detail=res.get("message"))
        
    return BookingResponse(
        success=res.get("success", False),
        message=res.get("message", ""),
        booking_id=res.get("booking_id")
    )

@router.get("/analytics/{session_id}", response_model=AnalyticsData)
async def analytics_endpoint(session_id: str):
    """
    GET /api/analytics/{session_id}
    Retrieves post-conversation metrics and structured analytics for the session.
    """
    return generate_analytics(session_id)

@router.post("/reset")
async def reset_endpoint(request: ResetRequest):
    """
    POST /api/reset
    Resets the conversation history for a session.
    """
    memory_service.clear_session(request.session_id)
    return {
        "status": "success",
        "message": f"Session {request.session_id} history cleared."
    }
