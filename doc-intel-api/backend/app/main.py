import io
import os
import time
import logging
from fastapi import FastAPI, UploadFile, File, HTTPException, Depends, Security, Request
from fastapi.security import APIKeyHeader
from pydantic import BaseModel
from typing import List, Optional

# Core text processing & vector storage
from pypdf import PdfReader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_core.embeddings import Embeddings
from langchain_core.documents import Document

# Official SDK and Rate Limiter dependencies
from google import genai
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

app = FastAPI(title="Production Document Intelligence API", version="4.0.0")
logger = logging.getLogger("uvicorn.error")

#  SET UP RATE LIMITER: Tracks visitors by their IP address
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

STORAGE_DIR = "./vector_stores"
os.makedirs(STORAGE_DIR, exist_ok=True)
MAX_FILE_SIZE_MB = 25

#  SET UP AUTHENTICATION: Looking for an 'X-API-KEY' inside incoming request headers
API_KEY_NAME = "X-API-Key"
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)

# This is the master password required by the frontend to talk to your backend
MASTER_API_KEY = "super_secure_portfolio_token_2026"

async def verify_api_key(api_key: str = Depends(api_key_header)):
    if not api_key or api_key != MASTER_API_KEY:
        raise HTTPException(status_code=403, detail="Invalid or missing API access authorization token.")
    return api_key

# Custom Embeddings Wrapper
class NativeGoogleEmbeddings(Embeddings):
    def __init__(self):
        self.client = genai.Client()
        self.model_name = "gemini-embedding-001"

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        embeddings = []
        for text in texts:
            response = self.client.models.embed_content(model=self.model_name, contents=text)
            embeddings.append(response.embeddings[0].values)
        return embeddings

    def embed_query(self, text: str) -> List[float]:
        response = self.client.models.embed_content(model=self.model_name, contents=text)
        return response.embeddings[0].values

embeddings = NativeGoogleEmbeddings()

class ChatRequest(BaseModel):
    filename: str
    question: str

# 1. DevOps Health Check (Public endpoint - no Auth needed)
@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": time.time(), "storage": "active"}

# 2. Secured List Documents Route
@app.get("/api/list-documents")
async def list_documents(api_key: str = Depends(verify_api_key)):
    if not os.path.exists(STORAGE_DIR):
        return {"documents": []}
    dirs = [d for d in os.listdir(STORAGE_DIR) if os.path.isdir(os.path.join(STORAGE_DIR, d))]
    return {"documents": dirs}

# 3. Secured & Rate-Limited Document Upload Indexing
@app.post("/api/index-document")
@limiter.limit("5/minute")  #  Prevents API Key resource exhaustion
async def index_document(request: Request, file: UploadFile = File(...), api_key: str = Depends(verify_api_key)):
    try:
        contents = await file.read()
        file_size_mb = len(contents) / (1024 * 1024)
        
        if file_size_mb > MAX_FILE_SIZE_MB:
            raise HTTPException(status_code=400, detail=f"File exceeds maximum size limit of {MAX_FILE_SIZE_MB}MB.")
        
        documents: List[Document] = []
        filename = file.filename
        
        if filename.endswith(".txt"):
            text = contents.decode("utf-8")
            documents.append(Document(page_content=text, metadata={"page": 1, "source": filename}))
            
        elif filename.endswith(".pdf"):
            pdf_stream = io.BytesIO(contents)
            pdf_reader = PdfReader(pdf_stream)
            for page_num, page in enumerate(pdf_reader.pages, start=1):
                page_text = page.extract_text()
                if page_text and page_text.strip():
                    documents.append(Document(page_content=page_text, metadata={"page": page_num, "source": filename}))
        else:
            raise HTTPException(status_code=400, detail="Unsupported file format.")

        if not documents:
            raise HTTPException(status_code=400, detail="Document text is empty or unextractable.")

        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=150)
        split_docs = text_splitter.split_documents(documents)
        total_chunks = len(split_docs)

        batch_size = 15
        doc_store_path = os.path.join(STORAGE_DIR, filename)
        vector_db = None

        for i in range(0, total_chunks, batch_size):
            current_batch = split_docs[i:i + batch_size]
            if vector_db is None:
                vector_db = FAISS.from_documents(current_batch, embeddings)
            else:
                vector_db.add_documents(current_batch)
            if i + batch_size < total_chunks:
                time.sleep(5)

        vector_db.save_local(doc_store_path)
        return {"status": "success", "filename": filename, "total_chunks": total_chunks}

    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Indexing processing crash: {str(e)}")

# 4. Secured & Rate-Limited Document AI Chat Room
@app.post("/api/chat")
@limiter.limit("20/minute") #  Protects LLM query generation limits
async def chat_document(request: Request, chat_req: ChatRequest, api_key: str = Depends(verify_api_key)):
    doc_store_path = os.path.join(STORAGE_DIR, chat_req.filename)
    if not os.path.exists(doc_store_path):
        raise HTTPException(status_code=404, detail="The requested document index context can't be found.")
    
    try:
        vector_db = FAISS.load_local(doc_store_path, embeddings, allow_dangerous_deserialization=True)
        docs = vector_db.similarity_search(chat_req.question, k=4)
        
        citations = []
        context_blocks = []
        for doc in docs:
            page_num = doc.metadata.get("page", "Unknown")
            context_blocks.append(f"[Source Page: {page_num}]\n{doc.page_content}")
            if page_num not in citations:
                citations.append(page_num)
                
        context = "\n\n".join(context_blocks)
        client = genai.Client()
        
        prompt = (
            f"You are an expert Enterprise Document Intelligence Assistant. Answer the question using only "
            f"the extracted document context below.\n\n"
            f"Context:\n{context}\n\nQuestion: {chat_req.question}\nAnswer:"
        )
        
        response = client.models.generate_content(model="gemini-2.5-flash", contents=prompt)
        return {"answer": response.text, "pages_cited": sorted(citations)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))