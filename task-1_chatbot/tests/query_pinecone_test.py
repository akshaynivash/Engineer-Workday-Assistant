import os
import pinecone
from dotenv import load_dotenv
from langchain_pinecone import Pinecone  # ✅ Correct Import
from langchain_ollama import OllamaEmbeddings

#  Load Environment Variables
load_dotenv()

PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
PINECONE_ENVIRONMENT = os.getenv("PINECONE_ENVIRONMENT")
PINECONE_INDEX_NAME = os.getenv("PINECONE_INDEX_NAME")

#  Initialize Pinecone
pinecone_client = pinecone.Pinecone(api_key=PINECONE_API_KEY)
index = pinecone_client.Index(PINECONE_INDEX_NAME)

#  Load Embeddings
embeddings = OllamaEmbeddings(model="llama2")

#  Create VectorStore
vectorstore = Pinecone(index, embeddings, text_key="text")

#  Run Query on Pinecone
query_text = input("🔍 Enter a query to test Pinecone retrieval: ")
retrieved_docs = vectorstore.similarity_search(query_text, k=5)  # 🔥 Get Top 5 Relevant Sections

#  Display Results
print("\n📖 **Top Retrieved Study Sections:**\n")
for i, doc in enumerate(retrieved_docs, 1):
    print(f"🔹 **Document {i}:** {doc.page_content[:500]}...\n")
