import logging
import sys
import os
from logging.handlers import RotatingFileHandler
from pythonjsonlogger import jsonlogger

def setup_logger(name="project", level="INFO") -> logging.Logger:
    logger = logging.getLogger(name)
    if logger.handlers:
        return logger

    logger.setLevel(level)
    os.makedirs("logs", exist_ok=True)

    # ✅ 콘솔 핸들러 (전체 로그)
    stream_handler = logging.StreamHandler(sys.stdout)
    stream_handler.setFormatter(jsonlogger.JsonFormatter('%(asctime)s %(levelname)s %(name)s %(message)s'))
    logger.addHandler(stream_handler)

    # ✅ 성공 로그 핸들러 (INFO만 기록)
    info_handler = RotatingFileHandler("logs/success.log", maxBytes=1_000_000, backupCount=5)
    info_handler.setLevel(logging.INFO)
    info_handler.addFilter(lambda record: record.levelno == logging.INFO)  # INFO만 필터링
    info_handler.setFormatter(jsonlogger.JsonFormatter('%(asctime)s %(levelname)s %(name)s %(message)s'))
    logger.addHandler(info_handler)

    # ✅ 실패/경고 로그 핸들러 (WARNING 이상 기록)
    error_handler = RotatingFileHandler("logs/error.log", maxBytes=1_000_000, backupCount=5)
    error_handler.setLevel(logging.WARNING)  # WARNING, ERROR, CRITICAL 포함
    error_handler.setFormatter(jsonlogger.JsonFormatter('%(asctime)s %(levelname)s %(name)s %(message)s'))
    logger.addHandler(error_handler)

    return logger

log = setup_logger()
