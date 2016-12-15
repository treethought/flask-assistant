import logging

logger = logging.getLogger('flask-assistant')
logger.addHandler(logging.StreamHandler())
if logger.level == logging.NOTSET:
    logger.setLevel(logging.WARN)


from .core import (
    Assistant
)

from .response import statement

