import json
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from app.config import settings
from app.services.memory_service import MemoryService

class AnalyticsData(BaseModel):
    session_id: str
    customer_name: Optional[str] = None
    contact_number: Optional[str] = None
    language_used: str  # English, Hindi, Hinglish
    configuration_interest: str  # "2 BHK", "3 BHK", "Both", "Undecided"
    budget_bracket: Optional[str] = None
    interest_level: str  # High, Medium, Low, Uninterested
    site_visit_status: str  # Booked, Pending, Failed, Declined
    booked_slot: Optional[str] = None
    follow_up_required: bool = False
    follow_up_time: Optional[str] = None
    opt_out: bool = False
    escalation_required: bool = False
    objections_raised: List[str] = []
    summary: str

def generate_analytics(session_id: str) -> AnalyticsData:
    """
    Analyzes conversation memory and extracts structured JSON metrics.
    Uses OpenAI Structured Output/JSON mode or fallback heuristic parsing.
    """
    memory_service = MemoryService()
    history = memory_service.get_history(session_id)
    opt_out_status = memory_service.is_opted_out(session_id)

    # 1. Safe default fallback object if history is empty
    if not history:
        return AnalyticsData(
            session_id=session_id,
            language_used="English",
            configuration_interest="Undecided",
            interest_level="Low",
            site_visit_status="Pending",
            opt_out=opt_out_status,
            summary="No conversation history available for this session."
        )

    # 2. Extract values with heuristic parser (works in mock environments or as a fallback)
    customer_name = None
    contact_number = None
    language_used = "English"
    configuration_interest = "Undecided"
    interest_level = "Medium"
    site_visit_status = "Pending"
    booked_slot = None
    follow_up_required = False
    objections_raised = []
    escalation_required = False
    budget_bracket = None

    # Reconstruct text for analysis
    full_text = ""
    for msg in history:
        role = msg.get("role")
        content = msg.get("content") or ""
        full_text += f"{role}: {content}\n"
        
        content_lower = content.lower()

        # Language detection
        if any(w in content_lower for w in ["kya", "hai", "bhai", "kitna", "batao", "milna"]):
            language_used = "Hinglish"
        elif any(w in content_lower for w in ["कितना", "क्या", "बताओ", "नमस्ते"]):
            language_used = "Hindi"

        # Objection detection
        if any(w in content_lower for w in ["price", "expensive", "costly", "rate", "price kya"]):
            if "High price objection" not in objections_raised:
                objections_raised.append("High price objection")
        if any(w in content_lower for w in ["distance", "far", "remote", "bahut dur"]):
            if "Location distance objection" not in objections_raised:
                objections_raised.append("Location distance objection")

        # Configuration interest
        if "2 bhk" in content_lower:
            configuration_interest = "2 BHK"
        elif "3 bhk" in content_lower:
            configuration_interest = "3 BHK"
        elif "both" in content_lower:
            configuration_interest = "Both"

        # Customer name/phone from tool calls or messages
        # If it's a tool call for book_site_visit
        if role == "tool" and msg.get("name") == "book_site_visit":
            try:
                res = json.loads(content)
                if res.get("success"):
                    site_visit_status = "Booked"
                    customer_name = res.get("customer_name") or customer_name
                    # Look up phone number in the tool call's content
                    booked_slot = f"{res.get('date')} at {res.get('time')}"
                    configuration_interest = res.get("configuration") or configuration_interest
                    interest_level = "High"
                else:
                    site_visit_status = "Failed"
                    follow_up_required = True
                    interest_level = "Medium"
            except Exception:
                pass

        # Try to extract phone number or customer name from user messages
        if role == "user":
            # Match 10+ digits for phone number
            import re
            phone_match = re.search(r'\b\d{10,}\b|\b\d{3}[-\s]?\d{3}[-\s]?\d{4}\b', content)
            if phone_match:
                contact_number = phone_match.group(0).replace("-", "").replace(" ", "")
            
            # Match name
            name_match = re.search(r'(?:name is|name:)\s*([A-Za-z\s]+?)(?:,|$|\.|\bphone\b|\bfor\b)', content, re.IGNORECASE)
            if name_match:
                customer_name = name_match.group(1).strip()
            else:
                name_fallback = re.search(r'(?:for|i am)\s+([A-Za-z\s]+?)(?:,|$|\.)', content, re.IGNORECASE)
                if name_fallback:
                    cand = name_fallback.group(1).strip()
                    if not any(x in cand.lower() for x in ["tomorrow", "today", "yesterday", "saturday", "sunday", "monday", "tuesday", "wednesday", "thursday", "friday", "visit", "year"]):
                        customer_name = cand

    if opt_out_status:
        site_visit_status = "Declined"
        interest_level = "Uninterested"

    # Determine if API call is possible
    api_key = settings.OPENAI_API_KEY
    is_mock = not api_key or api_key == "your_openai_api_key_here" or "mock" in api_key.lower()

    if not is_mock:
        try:
            from openai import OpenAI
            client = OpenAI(api_key=api_key)
            prompt = f"Analyze the following conversation history and extract structured analytics:\n\n{full_text}"
            
            response = client.beta.chat.completions.parse(
                model=settings.LLM_MODEL,
                messages=[
                    {"role": "system", "content": "You are a sales operations analyst. Extract structured metrics from conversation history."},
                    {"role": "user", "content": prompt}
                ],
                response_format=AnalyticsData
            )
            parsed_data = response.choices[0].message.parsed
            if parsed_data:
                return parsed_data
        except Exception:
            # Fallback to heuristic parser
            pass

    # Produce summary description for heuristic fallback
    summary_parts = []
    if customer_name:
        summary_parts.append(f"Customer {customer_name} initiated contact.")
    else:
        summary_parts.append("An anonymous customer initiated contact.")

    if site_visit_status == "Booked":
        summary_parts.append(f"Successfully booked a site visit for {booked_slot}.")
    elif site_visit_status == "Failed":
        summary_parts.append("Attempted to book site visit, but failed due to invalid inputs or slot unavailability.")
    elif opt_out_status:
        summary_parts.append("Customer requested to opt out.")
    else:
        summary_parts.append("Customer requested details about the project.")

    summary = " ".join(summary_parts)

    return AnalyticsData(
        session_id=session_id,
        customer_name=customer_name,
        contact_number=contact_number,
        language_used=language_used,
        configuration_interest=configuration_interest,
        budget_bracket=budget_bracket,
        interest_level=interest_level,
        site_visit_status=site_visit_status,
        booked_slot=booked_slot,
        follow_up_required=follow_up_required,
        follow_up_time=None,
        opt_out=opt_out_status,
        escalation_required=escalation_required,
        objections_raised=objections_raised,
        summary=summary
    )
