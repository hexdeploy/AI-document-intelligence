from pydantic import BaseModel
from typing import Optional

class ExecutionMetrics(BaseModel):
    execution_time_ms: float
    throughput_chars_per_sec: Optional[float] = None
    chunks_processed: Optional[int] = None