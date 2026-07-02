"""Seeds a predefined weekly schedule into ChromaDB on startup, if not already
present. Ported from the original task-1_chatbot/backend/chroma_db.py
(a manual, standalone script) -- now runs automatically and idempotently, so
the Schedule tool has real data without a separate manual step."""

SCHEDULE = {
    "Monday": (
        "Gym at 7 AM, Breakfast at 8 AM, Study Block from 10 AM - 12 PM, Lunch at 1 PM, "
        "Work from 2 PM - 6 PM, Dinner at 8 PM."
    ),
    "Tuesday": (
        "Gym at 6 AM, Study Block from 9 AM - 12 PM, Lunch at 1 PM, Work from 2 PM - 5 PM, "
        "Free Time in the evening."
    ),
    "Wednesday": (
        "Gym at 7 AM, Breakfast at 8 AM, Study from 10 AM - 1 PM, Lunch at 2 PM, Meeting at 4 PM, Dinner at 8 PM."
    ),
    "Thursday": "Gym at 6:30 AM, Work from 10 AM - 4 PM, Evening study session from 5 PM - 7 PM, Dinner at 9 PM.",
    "Friday": "Morning walk at 6 AM, Study from 9 AM - 12 PM, Work calls at 3 PM, Evening free time, Dinner at 8 PM.",
    "Saturday": "Brunch at 10 AM, Study AI topics from 12 PM - 2 PM, Hobby time in the evening.",
    "Sunday": "Full free day, light study from 3 PM - 5 PM, Movie night.",
}


def seed_schedule(schedule_collection) -> None:
    """Safe to call every startup -- skips if already populated."""
    if schedule_collection.count() > 0:
        return

    schedule_collection.add(
        ids=list(SCHEDULE.keys()),
        documents=[f"{day}: {plan}" for day, plan in SCHEDULE.items()],
        metadatas=[{"day": day} for day in SCHEDULE],
    )
