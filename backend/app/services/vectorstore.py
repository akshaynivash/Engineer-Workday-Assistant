"""Local FAISS-backed vector store for the study/general-chat RAG tools.

Uses FAISS (an embedded, local vector index) instead of Pinecone -- no cloud
account or API key needed. The only remaining external dependency for the
assistant is a locally running Ollama.
"""

from pathlib import Path

from app.data import REPO_ROOT

INDEX_DIR = REPO_ROOT / "data" / "faiss_index"
PDF_DIR = REPO_ROOT / "data" / "pdfs"
FALLBACK_PDF = REPO_ROOT / "Report.pdf"  # ships in the repo root; used if data/pdfs/ is empty
EMPTY_PLACEHOLDER = (
    "No study material has been indexed yet. Drop PDFs into data/pdfs/ and delete "
    "data/faiss_index/ to rebuild the index."
)


def _collect_pdf_paths() -> list[Path]:
    if PDF_DIR.is_dir():
        pdfs = sorted(PDF_DIR.glob("*.pdf"))
        if pdfs:
            return pdfs
    return [FALLBACK_PDF] if FALLBACK_PDF.exists() else []


def load_or_build_vectorstore(embeddings):
    """Loads a persisted FAISS index if one exists, otherwise builds one from
    whatever PDFs are available (data/pdfs/*.pdf, falling back to Report.pdf)
    and persists it for next time. Never raises -- falls back to a one-document
    placeholder index if no PDFs are found at all, so RAG tools still work
    (they'll just say nothing's indexed yet, instead of crashing).
    """
    from langchain_community.vectorstores import FAISS

    if INDEX_DIR.is_dir():
        return FAISS.load_local(str(INDEX_DIR), embeddings, allow_dangerous_deserialization=True)

    from langchain_community.document_loaders import PyPDFLoader
    from langchain_core.documents import Document
    from langchain_text_splitters import RecursiveCharacterTextSplitter

    pdf_paths = _collect_pdf_paths()
    if pdf_paths:
        documents = []
        for path in pdf_paths:
            documents.extend(PyPDFLoader(str(path)).load())
        splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
        chunks = splitter.split_documents(documents)
    else:
        chunks = [Document(page_content=EMPTY_PLACEHOLDER)]

    vectorstore = FAISS.from_documents(chunks, embeddings)
    vectorstore.save_local(str(INDEX_DIR))
    return vectorstore
