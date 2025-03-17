import os
import pinecone
from dotenv import load_dotenv
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_ollama import OllamaEmbeddings  #  Use Ollama instead of OpenAI
from langchain.vectorstores import Pinecone

#  Load Environment Variables
load_dotenv()

PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
PINECONE_ENVIRONMENT = os.getenv("PINECONE_ENVIRONMENT")
PINECONE_INDEX_NAME = os.getenv("PINECONE_INDEX_NAME")

#  Initialize Pinecone
pinecone_client = pinecone.Pinecone(api_key=PINECONE_API_KEY)

#  Load and Process the PDF
import os

pdf_path = "data/genai_book2.pdf"

# Check if PDF exists before processing
if not os.path.exists(pdf_path):
    raise FileNotFoundError(f"🚨 ERROR: PDF not found at {pdf_path}. Check the path!")

print(f"📂 PDF found: {pdf_path} ✅ Processing...")
 # Replace with actual path
loader = PyPDFLoader(pdf_path)
documents = loader.load()

#  Split Text into Chunks
text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
text_chunks = text_splitter.split_documents(documents)

#  Use Ollama for Embeddings
embeddings = OllamaEmbeddings(model="llama2")

#  Store Embeddings in Pinecone
vectorstore = Pinecone.from_documents(text_chunks, embeddings, index_name=PINECONE_INDEX_NAME)

print("🎉 PDF Data Successfully Uploaded to Pinecone using Ollama!")
