import logging

logger = logging.getLogger("flask_assistant")
handler = logging.StreamHandler()
formatter = logging.Formatter(
    "%(asctime)s:%(name)s:%(levelname)s: %(message)s", "%Y-%m-%d %H:%M:%S"
)
handler.setFormatter(formatter)
logger.addHandler(handler)


if logger.level == logging.NOTSET:
    logger.setLevel(logging.INFO)


from flask_assistant.core import (
    Assistant,
    context_manager,
    intent,
    request,
    access_token,
    user,
    storage,
    session_id,
    context_in,
)

from flask_assistant.response import ask, tell, event, build_item, permission
from flask_assistant.manager import Context

import flask_assistant.utils

from api_ai.api import ApiAi
