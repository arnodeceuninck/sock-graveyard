"""
Logging configuration for Sock Matcher ML Models

Provides a simple logger that can work standalone or integrate with backend logging.
"""

import logging
import sys
from typing import Optional


# Global logger instance
_logger: Optional[logging.Logger] = None


def setup_logger(name: str = "sock_matcher", level: int = logging.INFO) -> logging.Logger:
    """
    Setup and configure logger
    
    Args:
        name: Logger name
        level: Logging level
        
    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)
    
    # Only configure if not already configured
    if not logger.handlers:
        logger.setLevel(level)
        
        # Create console handler
        handler = logging.StreamHandler(sys.stdout)
        handler.setLevel(level)
        
        # Create formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        handler.setFormatter(formatter)
        
        # Add handler to logger
        logger.addHandler(handler)
    
    return logger


def get_logger() -> logging.Logger:
    """
    Get logger instance
    
    Returns:
        Logger instance
    """
    global _logger
    
    if _logger is None:
        _logger = setup_logger()
    
    return _logger


def set_logger(logger: logging.Logger):
    """
    Set custom logger instance (useful for backend integration)
    
    Args:
        logger: Custom logger instance
    """
    global _logger
    _logger = logger
