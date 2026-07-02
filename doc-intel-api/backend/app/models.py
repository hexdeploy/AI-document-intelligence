from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime
from database import Base

class DocumentLog(Base):
    __tablename__ = "document_logs"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, index=True)
    summary = Column(String)  # Stores a snippet or structural summary 
    status = Column(String)   # "SUCCESS" or "FAILED"
    created_at = Column(DateTime, default=datetime.utcnow)