from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.services.rag import RAGPipeline
from app.utils.benchmark import benchmark_execution

router = APIRouter(prefix="/api", tags=["Q&A Engine"])
rag_pipeline = RAGPipeline()

class AskRequest(BaseModel):
    question: str

@router.post("/ask")
async def ask_question(payload: AskRequest):
    if not payload.question.strip():
        raise HTTPException(status_code=400, detail="Question cannot be blank.")
    
    try:
        # Benchmark the RAG engine call using our new utility
        result, latency = benchmark_execution(rag_pipeline.answer_question, payload.question)
        
        return {
            "answer": result["answer"],
            "source_documents": result["source_documents"],
            "performance_metrics": {
                "execution_time_ms": latency,
                "engine": "RAG Retrieval + Gemini 2.5 Flash"
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"RAG processing failed: {str(e)}")