"""Metrics collection."""
import time
from typing import Dict, Any

class MetricsCollector:
    def __init__(self):
        self.requests = 0
        self.errors = 0
        self.total_time = 0.0
    
    def record_request_start(self, method: str, endpoint: str):
        self.requests += 1
    
    def record_request(self, method: str, endpoint: str, status_code: int, duration: float):
        """Record a complete request with all details"""
        self.requests += 1
        self.total_time += duration
        if status_code >= 400:
            self.errors += 1
    
    def record_request_success(self, response_time: float):
        self.total_time += response_time
    
    def record_request_error(self, error_type: str):
        self.errors += 1
    
    def record_circuit_breaker_trip(self):
        pass
    
    def record_circuit_breaker_reset(self):
        pass
    
    def get_summary(self) -> Dict[str, Any]:
        return {
            "total_requests": self.requests,
            "total_errors": self.errors,
            "success_rate": (self.requests - self.errors) / max(self.requests, 1) * 100,
            "average_response_time": self.total_time / max(self.requests, 1)
        }
    
    def measure_request(self, operation: str):
        return self
    
    def __enter__(self):
        self.start_time = time.time()
        return self
    
    def __exit__(self, *args):
        self.record_request_success(time.time() - self.start_time)
