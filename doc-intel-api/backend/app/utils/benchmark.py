import time
from typing import Tuple, Any

def benchmark_execution(func, *args, **kwargs) -> Tuple[Any, float]:
    """
    Executes a function and measures its latency in milliseconds.
    Returns a tuple of (function_result, execution_time_ms).
    """
    start_time = time.perf_counter()
    result = func(*args, **kwargs)
    end_time = time.perf_counter()
    
    execution_time_ms = round((end_time - start_time) * 1000, 2)
    return result, execution_time_ms