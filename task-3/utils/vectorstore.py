"""Local FAISS-backed vector store for the study/general-chat RAG tools.

Replaces Pinecone (a cloud account + API key) with FAISS (an embedded,
local vector index, no external service). The only remaining external
dependency for the Personal Assistant page is a locally running Ollama.
"""

import os
from pathlib import Path

INDEX_DIR = "data/faiss_index"
PDF_DIR = "data/pdfs"
FALLBACK_PDF = "Report.pdf"  # ships in the repo root; used if data/pdfs/ is empty
EMPTY_PLACEHOLDER = (
    "No study material has been indexed yet. Drop PDFs into data/pdfs/ and delete "
    "data/faiss_index/ to rebuild the index."
)


def _collect_pdf_paths() -> list[str]:
    pdf_dir = Path(PDF_DIR)
    if pdf_dir.is_dir():
        pdfs = [str(p) for p in sorted(pdf_dir.glob("*.pdf"))]
        if pdfs:
            return pdfs
    return [FALLBACK_PDF] if os.path.exists(FALLBACK_PDF) else []


def load_or_build_vectorstore(embeddings):
    """Loads a persisted FAISS index if one exists, otherwise builds one from
    whatever PDFs are available (data/pdfs/*.pdf, falling back to Report.pdf)
    and persists it for next time. Never raises -- falls back to a one-document
    placeholder index if no PDFs are found at all, so RAG tools still work
    (they'll just say nothing's indexed yet, instead of crashing).
    """
    from langchain_community.vectorstores import FAISS

    if os.path.isdir(INDEX_DIR):
        return FAISS.load_local(INDEX_DIR, embeddings, allow_dangerous_deserialization=True)

    from langchain.text_splitter import RecursiveCharacterTextSplitter
    from langchain_community.document_loaders import PyPDFLoader
    from langchain_core.documents import Document

    pdf_paths = _collect_pdf_paths()
    if pdf_paths:
        documents = []
        for path in pdf_paths:
            documents.extend(PyPDFLoader(path).load())
        splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
        chunks = splitter.split_documents(documents)
    else:
        chunks = [Document(page_content=EMPTY_PLACEHOLDER)]

    vectorstore = FAISS.from_documents(chunks, embeddings)
    vectorstore.save_local(INDEX_DIR)
    return vectorstore
