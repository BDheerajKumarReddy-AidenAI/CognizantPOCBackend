"""Logging configuration."""
import logging
import sys
from app.config import settings


def setup_logging() -> None:
    """Configure application logging with emojis for better visibility."""
    
    # Configure root logger
    logging.basicConfig(
        level=getattr(logging, settings.log_level.upper()),
        format='%(asctime)s - %(levelname)s - %(name)s - %(message)s',
        datefmt='%H:%M:%S',
        handlers=[
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    # Reduce noise from third-party libraries
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)
    logging.getLogger("openai").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    
    # Disable SQLAlchemy query logging (keep only warnings/errors)
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy.pool").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy.dialects").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy.orm").setLevel(logging.WARNING)


def get_logger(name: str) -> logging.Logger:
    """Get a logger instance for a module."""
    return logging.getLogger(name)


# Custom log format with emojis for key events
class EmojiFormatter(logging.Formatter):
    """Add emojis to log levels for better visibility."""
    
    EMOJI_MAP = {
        'DEBUG': '🔍',
        'INFO': '✅',
        'WARNING': '⚠️',
        'ERROR': '❌',
        'CRITICAL': '🚨'
    }
    
    def format(self, record):
        emoji = self.EMOJI_MAP.get(record.levelname, '')
        record.levelname = f"{emoji} {record.levelname}"
        return super().format(record)


def get_emoji_logger(name: str) -> logging.Logger:
    """Get a logger with emoji formatting."""
    logger = logging.getLogger(name)
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(EmojiFormatter(
        '%(asctime)s - %(levelname)s - %(name)s - %(message)s',
        datefmt='%H:%M:%S'
    ))
    logger.addHandler(handler)
    logger.propagate = False
    return logger
