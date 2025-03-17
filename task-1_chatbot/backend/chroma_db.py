import chromadb

# Initialize ChromaDB client
chroma_client = chromadb.PersistentClient(path="./data/chroma_db")

# Create or load a collection for schedules
schedule_collection = chroma_client.get_or_create_collection(name="daily_schedule")

def store_schedule():
    """Stores a predefined weekly schedule in ChromaDB."""
    schedule_collection.add(
        ids=[
            "monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"
        ],
        documents=[
            "Monday: Gym at 7 AM, Breakfast at 8 AM, Study Block from 10 AM - 12 PM, Lunch at 1 PM, Work from 2 PM - 6 PM, Dinner at 8 PM.",
            "Tuesday: Gym at 6 AM, Study Block from 9 AM - 12 PM, Lunch at 1 PM, Work from 2 PM - 5 PM, Free Time in the evening.",
            "Wednesday: Gym at 7 AM, Breakfast at 8 AM, Study from 10 AM - 1 PM, Lunch at 2 PM, Meeting at 4 PM, Dinner at 8 PM.",
            "Thursday: Gym at 6:30 AM, Work from 10 AM - 4 PM, Evening study session from 5 PM - 7 PM, Dinner at 9 PM.",
            "Friday: Morning walk at 6 AM, Study from 9 AM - 12 PM, Work calls at 3 PM, Evening free time, Dinner at 8 PM.",
            "Saturday: Brunch at 10 AM, Study AI topics from 12 PM - 2 PM, Hobby time in the evening.",
            "Sunday: Full free day, light study from 3 PM - 5 PM, Movie night."
        ],
        metadatas=[
            {"day": "Monday", "focus": "Study & Work"},
            {"day": "Tuesday", "focus": "Study & Free Time"},
            {"day": "Wednesday", "focus": "Meetings & Study"},
            {"day": "Thursday", "focus": "Work & Study"},
            {"day": "Friday", "focus": "Study & Free Time"},
            {"day": "Saturday", "focus": "Study & Hobbies"},
            {"day": "Sunday", "focus": "Relax & Light Study"}
        ]
    )
    print("✅ Schedule stored successfully!")

def retrieve_schedule(day):
    """Retrieve the schedule for a specific day."""
    results = schedule_collection.query(query_texts=[day], n_results=1)
    return results["documents"][0] if results["documents"] else "No schedule found."
# Store the schedule (call this once to populate the collection)
store_schedule()