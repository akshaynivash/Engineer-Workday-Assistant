import os
from pinecone import Pinecone
from dotenv import load_dotenv

#  Load API Key from .env
load_dotenv()
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")

# Initialize Pinecone
pc = Pinecone(api_key=PINECONE_API_KEY)

#  List available indexes
indexes = pc.list_indexes().names()
print("📌 Available Pinecone Indexes:", indexes)

#  Check connection
if indexes:
    print(f"Pinecone is connected! Available indexes: {indexes}")
else:
    print(" No Pinecone indexes found. Create one in the Pinecone dashboard.")
