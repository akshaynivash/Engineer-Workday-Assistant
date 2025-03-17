import os
from dotenv import load_dotenv
from pinecone import Pinecone
from langchain_pinecone import PineconeVectorStore
from langchain_ollama import OllamaEmbeddings
from langchain.chains import RetrievalQA

#  Load environment variables
load_dotenv()

PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
PINECONE_INDEX_NAME = os.getenv("PINECONE_INDEX_NAME")

#  Initialize Pinecone
pc = Pinecone(api_key=PINECONE_API_KEY)

#  Connect to Pinecone index
index = pc.Index(PINECONE_INDEX_NAME)

#  Use Ollama for embeddings
embeddings = OllamaEmbeddings(model="llama2")

#  Create Pinecone VectorStore
vectorstore = PineconeVectorStore(
    index=index,
    embedding_function=embeddings,
    text_key="text",   # name of the field in your Pinecone index that contains text
)

#  Function to Generate Quiz (or Q&A) from Pinecone Data
def generate_quiz_from_pinecone(query: str) -> str:
    """
    Retrieves relevant content from Pinecone and generates a quiz or Q&A response
    using the Ollama Llama 2 model via LangChain.
    """
    retriever = vectorstore.as_retriever()
    qa_chain = RetrievalQA.from_chain_type(llm=embeddings, retriever=retriever)

    response = qa_chain.run(query)
    return response
