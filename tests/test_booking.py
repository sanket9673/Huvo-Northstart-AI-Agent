import pytest
from app.services.booking_service import book_site_visit
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_booking_success():
    res = book_site_visit(
        customer_name="Sanket Chavhan",
        phone_number="9876543210",
        preferred_date="2026-08-20",
        preferred_time="11:00 AM",
        configuration_interest="3 BHK"
    )
    assert res["success"] is True
    assert "booking_id" in res
    assert res["booking_id"].startswith("NSV-")
    assert res["date"] == "2026-08-20"
    assert res["time"] == "11:00 AM"
    assert res["configuration"] == "3 BHK"
    assert "Site visit successfully booked" in res["message"]

def test_booking_invalid_phone():
    # Phone number has less than 10 digits
    res = book_site_visit(
        customer_name="Sanket Chavhan",
        phone_number="987654",
        preferred_date="2026-08-20",
        preferred_time="11:00 AM"
    )
    assert res["success"] is False
    assert res["error_type"] == "INVALID_PHONE"
    assert "10-digit phone number" in res["message"]

def test_booking_past_year():
    # Date contains a past year
    res = book_site_visit(
        customer_name="Sanket Chavhan",
        phone_number="9876543210",
        preferred_date="2023-08-20",
        preferred_time="11:00 AM"
    )
    assert res["success"] is False
    assert res["error_type"] == "SLOT_UNAVAILABLE"

def test_booking_fail_trigger():
    # Date contains FAIL trigger
    res = book_site_visit(
        customer_name="Sanket Chavhan",
        phone_number="9876543210",
        preferred_date="FAIL",
        preferred_time="11:00 AM"
    )
    assert res["success"] is False
    assert res["error_type"] == "SLOT_UNAVAILABLE"

def test_booking_past_date():
    # Specific past date
    res = book_site_visit(
        customer_name="Sanket Chavhan",
        phone_number="9876543210",
        preferred_date="2025-01-01",
        preferred_time="11:00 AM"
    )
    assert res["success"] is False
    assert res["error_type"] == "SLOT_UNAVAILABLE"

def test_api_booking_endpoint():
    response = client.post("/api/booking", json={
        "customer_name": "John Doe",
        "phone_number": "9999999999",
        "preferred_date": "2026-09-01",
        "preferred_time": "02:00 PM",
        "configuration_interest": "2 BHK"
    })
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "booking_id" in data
