import uuid
from fastapi import APIRouter, UploadFile, File, HTTPException
from app.services.parser import DocumentParser
from app.services.vector_store import VectorStoreManager
from app.services.embedder import DocumentEmbedder
from app.models.schemas import UploadResponse

router = APIRouter(prefix="/api", tags=["Upload"])
vector_manager = VectorStoreManager()

@router.post("/upload", response_model=UploadResponse)
async def upload_document(file: UploadFile = File(...)):
    if not file.filename.endswith(('.pdf', '.txt')):
        raise HTTPException(status_code=400, detail="Unsupported file format. Please upload a PDF or TXT file.")
    
    try:
        file_bytes = await file.read()
        
        if file.filename.endswith('.pdf'):
            text, pages = DocumentParser.parse_pdf(file_bytes)
        else:
            text, pages = DocumentParser.parse_txt(file_bytes)
            
        if not text:
            raise HTTPException(status_code=400, detail="The provided document contains no extractable text.")
            
        document_id = str(uuid.uuid4())
        
        # Trigger text chunking and generation
        embedder = DocumentEmbedder()
        chunks = embedder.chunk_text(text)
        vector_manager.create_stores(chunks, document_id)
        
        preview = text[:200] + "..." if len(text) > 200 else text
        
        return UploadResponse(
            filename=file.filename,
            page_count=pages,
            preview=preview,
            message=f"File split into {len(chunks)} chunks and vectorized successfully into local stores."
        )
    except Exception as e:
        # This logs the exact hidden issue to your console terminal so we can see it instantly
        print(f"❌ CRITICAL UPLOAD ROUTE ERROR: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Upload indexing failed: {str(e)}")