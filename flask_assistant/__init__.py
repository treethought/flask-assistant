import logging

logger = logging.getLogger('flask_assistant')
logger.addHandler(logging.StreamHandler())
if logger.level == logging.NOTSET:
    logger.setLevel(logging.INFO)


from .core import (
    Assistant,
    context_manager
)

from .response import ask, tell
from .manager import Context
