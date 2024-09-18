from __future__ import annotations

from datetime import datetime
import sys
from typing import Optional
from loguru import logger
import loguru

from src.config import settings

_logger_instance: Optional[loguru.Logger] = None

log_format = \
    "<white>{time:YYYY-MM-DD HH:mm:ss}</white>"\
    " | <level>{level: <8}</level>"\
    " | <cyan><b>{line}</b></cyan>"\
    " - <white><b>{extra[session_name]}</b></white>"\
    " | <white><b>{message}</b></white>"


def _add_file_sink(logger_instance):
    file_name = datetime.now().strftime("./logs/log-%d-%m.log")

    logger_instance.add(file_name,
        format=log_format,
        level="TRACE",
        backtrace=True,
        diagnose=True,
        rotation="5 MB"
    )

def _configure_logger() -> loguru.Logger:
    global _logger_instance
    
    if _logger_instance:
        return _logger_instance

    logger.remove() # Remove default handlers to prevent duplicates

    log_level = "DEBUG" if settings.DEBUG_MODE else "INFO"
    
    logger.add(sys.stdout,
        format=log_format,
        colorize=False,
        level=log_level,
        backtrace=True,
        diagnose=True
    )

    _add_file_sink(logger)

    _logger_instance = logger
    return _logger_instance
    

def get_logger(session_name: str = "") -> loguru.Logger:
    _logger_instance = _configure_logger()

    bound_logger = _logger_instance.bind(session_name=session_name)
    return bound_logger