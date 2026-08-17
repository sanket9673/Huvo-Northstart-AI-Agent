from pydantic import BaseModel
from typing import Dict, Any, Optional

class ChatRequest(BaseModel):
    session_id: str
    message: str

class ChatResponse(BaseModel):
    session_id: str
    response: str
    booking_details: Optional[Dict[str, Any]] = None
    opt_out: bool = False

class BookingRequest(BaseModel):
    customer_name: str
    phone_number: str
    preferred_date: str
    preferred_time: str
    configuration_interest: Optional[str] = "Unspecified"

class BookingResponse(BaseModel):
    success: bool
    message: str
    booking_id: Optional[str] = None

class ResetRequest(BaseModel):
    session_id: str
