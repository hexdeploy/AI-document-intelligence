# app/models/schemas.py
from pydantic import BaseModel

class UploadResponse(BaseModel):
    filename: str
    page_count: int
    preview: str
    message: str
    
class QueryRequest(BaseModel):
    question: str

class QueryResponse(BaseModel):
    answer: str
    source_chunks: list[str]