import logging

from ..settings import DEFAULT_LOG_LEVEL, MAIN_LOG_FILE

logging.basicConfig(filename=MAIN_LOG_FILE)

def get_logger(name, level=DEFAULT_LOG_LEVEL):
    logger = logging.getLogger(name)

    logLevel = getattr(logging, level)
    logger.setLevel(logLevel)


    return logger
