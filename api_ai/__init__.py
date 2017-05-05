import logging

logger = logging.getLogger('api_ai')
logger.addHandler(logging.StreamHandler())
if logger.level == logging.NOTSET:
    logger.setLevel(logging.INFO)