"""
結構化日誌：含時間戳 + 模組名稱，同時寫入 logs/ 資料夾
"""
import logging
import sys
from pathlib import Path
from datetime import datetime

from src.config import LOGS_DIR

LOGS_DIR.mkdir(parents=True, exist_ok=True)

_fmt = "%(asctime)s | %(levelname)-8s | %(name)-20s | %(message)s"
_date_fmt = "%Y-%m-%d %H:%M:%S"


def get_logger(name: str) -> logging.Logger:
    logger = logging.getLogger(name)

    if logger.handlers:
        return logger

    logger.setLevel(logging.DEBUG)

    # Console handler（強制 UTF-8，避免 Windows cp950 亂碼）
    import io
    stream = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace") if hasattr(sys.stdout, "buffer") else sys.stdout
    console = logging.StreamHandler(stream)
    console.setLevel(logging.INFO)
    console.setFormatter(logging.Formatter(_fmt, _date_fmt))

    # File handler（每日一個 log 檔）
    log_file = LOGS_DIR / f"{datetime.now().strftime('%Y-%m-%d')}.log"
    file_handler = logging.FileHandler(log_file, encoding="utf-8")
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(logging.Formatter(_fmt, _date_fmt))

    logger.addHandler(console)
    logger.addHandler(file_handler)

    return logger
