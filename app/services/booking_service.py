import datetime
import random
from typing import Dict, Any, List

# In-memory database of recorded bookings
_bookings: List[Dict[str, Any]] = []

def book_site_visit(
    customer_name: str,
    phone_number: str,
    preferred_date: str,
    preferred_time: str,
    configuration_interest: str = "Unspecified"
) -> Dict[str, Any]:
    """
    Simulates site-visit booking for Northstar One with phone number and date validations.
    """
    # 1. Phone number validation (must contain at least 10 digits)
    digits_count = sum(1 for c in phone_number if c.isdigit())
    if digits_count < 10:
        return {
            "success": False,
            "error_type": "INVALID_PHONE",
            "message": "Invalid contact number provided. Please provide a valid 10-digit phone number."
        }

    # 2. Date validations
    date_lower = preferred_date.lower()
    # Check for past years or specific failure trigger keywords
    if any(yr in date_lower for yr in ["2020", "2021", "2022", "2023", "2024"]) or "full" in date_lower or "fail" in date_lower:
        return {
            "success": False,
            "error_type": "SLOT_UNAVAILABLE",
            "message": "The requested date/slot is unavailable or invalid. Please request an alternate date or offer a manual call back."
        }

    # Try parsing dates to check if they are in the past
    # (Since current date is Aug 17, 2026, we check if it is before that)
    for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%m/%d/%Y", "%Y/%m/%d", "%d-%m-%Y"):
        try:
            parsed_date = datetime.datetime.strptime(preferred_date.strip(), fmt).date()
            if parsed_date < datetime.date.today():
                return {
                    "success": False,
                    "error_type": "SLOT_UNAVAILABLE",
                    "message": "The requested date/slot is unavailable or invalid. Please request an alternate date or offer a manual call back."
                }
            break
        except ValueError:
            continue

    # 3. Success path: Generate a random booking ID and record
    booking_num = random.randint(10000, 99999)
    booking_id = f"NSV-{booking_num}"
    
    booking_record = {
        "success": True,
        "booking_id": booking_id,
        "customer_name": customer_name,
        "phone_number": phone_number,
        "date": preferred_date,
        "time": preferred_time,
        "configuration": configuration_interest,
        "message": "Site visit successfully booked!"
    }
    
    _bookings.append(booking_record)
    
    return {
        "success": True,
        "booking_id": booking_id,
        "customer_name": customer_name,
        "date": preferred_date,
        "time": preferred_time,
        "configuration": configuration_interest,
        "message": "Site visit successfully booked!"
    }

BOOKING_TOOL_SPEC = {
    "type": "function",
    "function": {
        "name": "book_site_visit",
        "description": "Book a site visit for Northstar One project in Sector 79 Gurugram once customer provides name, phone, preferred date and time.",
        "parameters": {
            "type": "object",
            "properties": {
                "customer_name": {"type": "string", "description": "Customer's full name"},
                "phone_number": {"type": "string", "description": "10-digit contact number"},
                "preferred_date": {"type": "string", "description": "Date for site visit (e.g. 2026-08-20 or 'Tomorrow')"},
                "preferred_time": {"type": "string", "description": "Time slot for visit (e.g. '11:00 AM')"},
                "configuration_interest": {"type": "string", "enum": ["2 BHK", "3 BHK", "Both", "Unspecified"], "description": "BHK configuration of interest"}
            },
            "required": ["customer_name", "phone_number", "preferred_date", "preferred_time"]
        }
    }
}
