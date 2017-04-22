import logging

logger = logging.getLogger('flask_assistant')
logger.addHandler(logging.StreamHandler())
if logger.level == logging.NOTSET:
    logger.setLevel(logging.INFO)


from flask_assistant.core import (
    Assistant,
    context_manager
)

from bot_framework.bot import Bot
from bot_framework.connector import reply


from flask_assistant.response import ask, tell, event
from flask_assistant.manager import Context
