import logging
import json
import sys
from datetime import datetime
from app.core.config import settings

class JSONFormatter(logging.Formatter):
    """
    Structured JSON log formatter for production observability.
    Converts log records into formatted JSON lines.
    """
    def format(self, record: logging.LogRecord) -> str:
        log_object = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "environment": settings.ENVIRONMENT,
            "module": record.module,
            "line_no": record.lineno
        }
        
        if record.exc_info:
            log_object["exception"] = self.formatException(record.exc_info)
            
        if hasattr(record, "extra_data"):
            log_object["extra"] = record.extra_data
            
        return json.dumps(log_object)

def setup_logging():
    """
    Sets up structured logging for the application.
    """
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    
    # Remove existing handlers
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
        
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(JSONFormatter())
    root_logger.addHandler(handler)

    # Silence overly verbose third-party loggers
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("botocore").setLevel(logging.WARNING)
