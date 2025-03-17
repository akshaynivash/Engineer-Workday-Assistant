import os
import pinecone
from dotenv import load_dotenv
from langchain.chains import RetrievalQA
from langchain_pinecone import Pinecone  #  Corrected Import
from langchain_ollama import OllamaLLM, OllamaEmbeddings  # Corrected Import

#  Load Environment Variables
load_dotenv()

PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
PINECONE_ENVIRONMENT = os.getenv("PINECONE_ENVIRONMENT")
PINECONE_INDEX_NAME = os.getenv("PINECONE_INDEX_NAME")

# Initialize Pinecone
pinecone_client = pinecone.Pinecone(api_key=PINECONE_API_KEY)
index = pinecone_client.Index(PINECONE_INDEX_NAME)

#  Load Llama 2 Model via Ollama
llama = OllamaLLM(model="llama2")  # 🚀 Updated Ollama Call

#  Load Ollama Embeddings
embeddings = OllamaEmbeddings(model="llama2")

#  Create Pinecone VectorStore (with Required `text_key`)
vectorstore = Pinecone(index, embeddings, text_key="text")  # ✅ Fix Missing Argument

#  Build a Retrieval-Augmented Generation (RAG) Chain
qa = RetrievalQA.from_chain_type(llm=llama, chain_type="stuff", retriever=vectorstore.as_retriever())

#  Ask Question
query_text = input("🤖 Ask AI anything about your study materials: ")
response = qa.run(query_text)

#  Print AI Explanation
print("\n🎓 AI Explanation:")
print(response)
