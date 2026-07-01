from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from app.services.insights import InsightsProcessor

router = APIRouter(prefix="/api", tags=["Document Insights"])
processor = InsightsProcessor()

# 🛠️ Robust schema tracking for incoming payloads
class InsightsRequest(BaseModel):
    text_content: str = Field(..., description="The raw string content extracted from your document.")

@router.post("/insights")
async def get_document_insights(payload: InsightsRequest):
    # Ensure text isn't empty or full of blank spaces
    cleaned_text = payload.text_content.strip()
    if not cleaned_text:
        raise HTTPException(status_code=400, detail="Text content cannot be blank.")
    
    try:
        insights = processor.extract_document_insights(cleaned_text)
        return insights
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Insights processing engine failed: {str(e)}")