# src/utils.py
import logging
from functools import wraps

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def setup_logger(name):
    logger = logging.getLogger(name)
    return logger

def error_handler(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            logger = setup_logger(func.__name__)
            logger.error(f"Error in {func.__name__}: {str(e)}")
            raise
    return wrapper