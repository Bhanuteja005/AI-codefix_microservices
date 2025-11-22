"""
Utility: Logger
Tracks token usage and latency metrics
"""
import csv
import os
import time
from datetime import datetime
from typing import Dict, Any
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MetricsLogger:
    """Logs token usage and latency metrics"""
    
    def __init__(self, log_file: str = "metrics_log.csv"):
        """
        Initialize the metrics logger
        
        Args:
            log_file: Path to the CSV log file
        """
        self.log_file = log_file
        self._initialize_log_file()
    
    def _initialize_log_file(self):
        """Create the log file with headers if it doesn't exist"""
        if not os.path.exists(self.log_file):
            with open(self.log_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow([
                    'timestamp',
                    'language',
                    'cwe',
                    'input_tokens',
                    'output_tokens',
                    'total_tokens',
                    'latency_ms',
                    'model_used',
                    'rag_enabled'
                ])
            logger.info(f"Created metrics log file: {self.log_file}")
    
    def log_request(self, metrics: Dict[str, Any]):
        """
        Log a single request's metrics
        
        Args:
            metrics: Dictionary containing metric values
        """
        timestamp = datetime.now().isoformat()
        
        # Extract values with defaults
        language = metrics.get('language', 'unknown')
        cwe = metrics.get('cwe', 'unknown')
        input_tokens = metrics.get('input_tokens', 0)
        output_tokens = metrics.get('output_tokens', 0)
        total_tokens = input_tokens + output_tokens
        latency_ms = metrics.get('latency_ms', 0)
        model_used = metrics.get('model_used', 'unknown')
        rag_enabled = metrics.get('rag_enabled', False)
        
        # Write to CSV
        try:
            with open(self.log_file, 'a', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow([
                    timestamp,
                    language,
                    cwe,
                    input_tokens,
                    output_tokens,
                    total_tokens,
                    latency_ms,
                    model_used,
                    rag_enabled
                ])
            
            # Also log to console
            logger.info(
                f"Request logged - Language: {language}, CWE: {cwe}, "
                f"Tokens: {input_tokens}/{output_tokens}, "
                f"Latency: {latency_ms}ms, Model: {model_used}"
            )
            
        except Exception as e:
            logger.error(f"Failed to log metrics: {str(e)}")
    
    def get_summary_stats(self) -> Dict[str, Any]:
        """
        Get summary statistics from the log
        
        Returns:
            Dictionary with summary statistics
        """
        if not os.path.exists(self.log_file):
            return {}
        
        try:
            with open(self.log_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                rows = list(reader)
            
            if not rows:
                return {}
            
            total_requests = len(rows)
            avg_latency = sum(float(r['latency_ms']) for r in rows) / total_requests
            avg_input_tokens = sum(int(r['input_tokens']) for r in rows) / total_requests
            avg_output_tokens = sum(int(r['output_tokens']) for r in rows) / total_requests
            
            return {
                'total_requests': total_requests,
                'avg_latency_ms': round(avg_latency, 2),
                'avg_input_tokens': round(avg_input_tokens, 2),
                'avg_output_tokens': round(avg_output_tokens, 2)
            }
            
        except Exception as e:
            logger.error(f"Failed to compute summary stats: {str(e)}")
            return {}


# Singleton instance
_logger_instance = None


def get_logger_instance(log_file: str = "metrics_log.csv") -> MetricsLogger:
    """Get or create the logger singleton instance"""
    global _logger_instance
    
    if _logger_instance is None:
        _logger_instance = MetricsLogger(log_file)
    
    return _logger_instance


class Timer:
    """Context manager for timing operations"""
    
    def __init__(self):
        self.start_time = None
        self.end_time = None
        self.elapsed_ms = None
    
    def __enter__(self):
        self.start_time = time.time()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.end_time = time.time()
        self.elapsed_ms = int((self.end_time - self.start_time) * 1000)
