import logging
import sys
from typing import Optional

def setup_logging(level: str = "INFO") -> None:
    """Configure logging for the entire mlhq package.
    
    Args:
        level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    """
    # Validate log level
    level = level.upper()
    if level not in ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']:
        raise ValueError(f"Invalid log level: {level}")
    
    # Configure root logger for the mlhq package
    logger = logging.getLogger('mlhq')
    logger.setLevel(getattr(logging, level))
    
    # Remove any existing handlers to avoid duplicates
    logger.handlers.clear()
    
    # Create console handler
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(getattr(logging, level))
    
    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    handler.setFormatter(formatter)
    
    # Add handler to logger
    logger.addHandler(handler)
    
    # Prevent propagation to root logger to avoid duplicate messages
    logger.propagate = False

def get_logger(name: str) -> logging.Logger:
    """Get a logger for the given module name.
    
    Args:
        name: Usually __name__ from the calling module
        
    Returns:
        Configured logger instance
    """
    return logging.getLogger(f'mlhq.{name.split(".")[-1]}')
