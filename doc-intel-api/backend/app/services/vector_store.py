import os
from langchain_community.vectorstores import FAISS
from langchain_community.vectorstores import Chroma
from app.services.embedder import DocumentEmbedder

FAISS_INDEX_DIR = "local_faiss_index"
CHROMA_DIR = "local_chroma_db"

class VectorStoreManager:
    def __init__(self):
        self.embedder = DocumentEmbedder()
        self.faiss_store = None

    def create_stores(self, text_chunks: list[str], document_id: str):
        """Indexes text chunks into FAISS memory and persists them down to Chroma."""
        embeddings = self.embedder.get_embeddings_engine()
        
        # 1. Build local FAISS Index
        self.faiss_store = FAISS.from_texts(text_chunks, embeddings)
        self.faiss_store.save_local(FAISS_INDEX_DIR)
        
        # 2. Persist to ChromaDB as backup validation layer
        chroma_store = Chroma.from_texts(
            texts=text_chunks,
            embedding=embeddings,
            persist_directory=CHROMA_DIR,
            collection_name=f"doc_{document_id.replace('-', '_')}"
        )
        return len(text_chunks)

    def get_retriever(self):
        """Loads and surfaces the primary FAISS index vector query retriever interface."""
        embeddings = self.embedder.get_embeddings_engine()
        if os.path.exists(FAISS_INDEX_DIR):
            self.faiss_store = FAISS.load_local(FAISS_INDEX_DIR, embeddings, allow_dangerous_deserialization=True)
        else:
            raise ValueError("No documents have been vectorized yet. Please upload a file first.")
        
        return self.faiss_store.as_retriever(search_kwargs={"k": 4})