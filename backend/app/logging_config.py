"""
Structured JSON logging configuration for the application.
Provides utilities for consistent JSON logging with context and trace correlation.
"""
import json
import logging
import sys
import traceback
from datetime import datetime
from typing import Any, Dict, Optional
from contextvars import ContextVar

# Context var to store trace IDs for log correlation
trace_id_var: ContextVar[Optional[str]] = ContextVar('trace_id', default=None)
span_id_var: ContextVar[Optional[str]] = ContextVar('span_id', default=None)


class JSONFormatter(logging.Formatter):
    """Custom formatter that outputs logs as JSON."""
    
    def format(self, record: logging.LogRecord) -> str:
        log_data = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        
        # Add trace context if available
        trace_id = trace_id_var.get()
        span_id = span_id_var.get()
        if trace_id:
            log_data["trace_id"] = trace_id
        if span_id:
            log_data["span_id"] = span_id
        
        # Add extra fields if present
        if hasattr(record, 'extra_fields'):
            log_data.update(record.extra_fields)
        
        # Add exception info if present
        if record.exc_info:
            log_data["exc_type"] = record.exc_info[0].__name__
            log_data["exc_message"] = str(record.exc_info[1])
            log_data["stack_trace"] = traceback.format_exception(*record.exc_info)
        
        return json.dumps(log_data)


def setup_logging(service_name: str = "backend", level: str = "INFO") -> logging.Logger:
    """
    Configure root logger with JSON formatting.
    
    Args:
        service_name: Name of the service for logging context
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    
    Returns:
        Configured logger instance
    """
    # Get root logger
    logger = logging.getLogger(service_name)
    logger.setLevel(getattr(logging, level.upper()))
    
    # Remove existing handlers to avoid duplicates
    logger.handlers.clear()
    
    # Create handler with JSON formatter
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(JSONFormatter())
    logger.addHandler(handler)
    
    # Don't propagate to root to avoid duplicate logs
    logger.propagate = False
    
    return logger


def log_with_context(
    logger: logging.Logger,
    level: str,
    message: str,
    **extra_fields: Any
) -> None:
    """
    Log a message with additional context fields.
    
    Args:
        logger: Logger instance
        level: Log level (info, warning, error, etc.)
        message: Log message
        **extra_fields: Additional fields to include in the JSON log
    """
    log_func = getattr(logger, level.lower())
    
    # Create a LogRecord with extra fields
    extra = {"extra_fields": extra_fields}
    log_func(message, extra=extra)


def log_error(
    logger: logging.Logger,
    message: str,
    exc: Optional[Exception] = None,
    **extra_fields: Any
) -> None:
    """
    Log an error with optional exception and context.
    
    Args:
        logger: Logger instance
        message: Error message
        exc: Exception instance (optional)
        **extra_fields: Additional context fields
    """
    extra = {"extra_fields": extra_fields}
    
    if exc:
        logger.error(message, exc_info=exc, extra=extra)
    else:
        logger.error(message, extra=extra)


def log_request(
    logger: logging.Logger,
    method: str,
    path: str,
    status_code: int,
    duration_ms: float,
    **extra_fields: Any
) -> None:
    """
    Log an HTTP request with timing information.
    
    Args:
        logger: Logger instance
        method: HTTP method
        path: Request path
        status_code: Response status code
        duration_ms: Request duration in milliseconds
        **extra_fields: Additional context fields
    """
    fields = {
        "event": "http_request",
        "method": method,
        "path": path,
        "status_code": status_code,
        "duration_ms": round(duration_ms, 2),
        **extra_fields
    }
    
    log_with_context(logger, "info", f"{method} {path} {status_code}", **fields)


def log_db_query(
    logger: logging.Logger,
    query_type: str,
    table: str,
    duration_ms: float,
    **extra_fields: Any
) -> None:
    """
    Log a database query with timing.
    
    Args:
        logger: Logger instance
        query_type: Type of query (SELECT, INSERT, UPDATE, DELETE)
        table: Table name
        duration_ms: Query duration in milliseconds
        **extra_fields: Additional context fields
    """
    fields = {
        "event": "db_query",
        "query_type": query_type,
        "table": table,
        "duration_ms": round(duration_ms, 2),
        **extra_fields
    }
    
    log_with_context(logger, "info", f"DB {query_type} on {table}", **fields)
