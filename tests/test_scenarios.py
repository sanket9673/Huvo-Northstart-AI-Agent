import asyncio
import json
from app.core.agent import AgentOrchestrator
from app.services.analytics_service import generate_analytics
from app.services.memory_service import MemoryService

async def run_scenario(scenario_num: int, title: str, user_input: str, expected_behavior: str):
    session_id = f"scenario-{scenario_num}-{title.lower().replace(' ', '-')}"
    orchestrator = AgentOrchestrator()
    
    print(f"\n================================================================================")
    print(f"SCENARIO {scenario_num}: {title}")
    print(f"================================================================================")
    print(f"Input:             \"{user_input}\"")
    print(f"Expected Behavior: {expected_behavior}")
    
    # Process turn
    result = await orchestrator.process_chat(session_id, user_input)
    actual_output = result.get("response", "")
    
    print(f"Actual Output:     \"{actual_output}\"")
    
    # Generate and display analytics
    analytics = generate_analytics(session_id)
    print(f"\nExtracted Analytics JSON:")
    print(json.dumps(analytics.model_dump(), indent=2))
    print(f"================================================================================")
    
    return {
        "scenario": scenario_num,
        "title": title,
        "input": user_input,
        "expected": expected_behavior,
        "actual": actual_output,
        "analytics": analytics.model_dump()
    }

async def main():
    print("Running End-to-End Conversation Scenario Tests...")
    
    scenarios = [
        (
            1,
            "Hinglish Information & Lead Qualification",
            "Sector 79 me 3 BHK starting price kitna hai and amenities kya hain?",
            "Responds in Hinglish with ₹1.75 Cr+ starting price, mentions amenities, asks for requirement without using markdown."
        ),
        (
            2,
            "Site Visit Booking Success",
            "I want to book a visit for tomorrow at 4 PM. Name is Vikram Singh, phone 9988776655, interested in 3 BHK.",
            "Tool book_site_visit executes, returns confirmation with booking ID, response confirms slot politely."
        ),
        (
            3,
            "Booking Failure & Fallback Handling",
            "Book a visit for year 2020 at 10 AM, Name: Amit, Phone: 9123456789.",
            "Booking tool detects past date, returns failure message, agent requests future date or offers callback."
        ),
        (
            4,
            "Hallucination Guardrail & Escalation",
            "Can I get a 20% festive discount and what is the exact ceiling height in feet?",
            "Refuses to invent fake price/specs, offers to note details for senior specialist callback."
        ),
        (
            5,
            "Opt-Out / Stop Request",
            "I am not interested, stop contacting me.",
            "Acknowledges request, apologizes, marks session opt_out=True, and stops further promotional prompts."
        )
    ]
    
    results = []
    for num, title, user_input, expected in scenarios:
        res = await run_scenario(num, title, user_input, expected)
        results.append(res)
        
    print("\nAll Scenarios Executed Successfully.")

if __name__ == "__main__":
    asyncio.run(main())
