from __future__ import absolute_import
import os
import sys
import logging
from flask_assistant.core import Assistant
from . import logger


logger.setLevel(logging.INFO)


def import_with_3(module_name, path):
    import importlib.util
    spec = importlib.util.spec_from_file_location(module_name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def import_with_2(module_name, path):
    import imp
    return imp.load_source(module_name, path)


def get_assistant(filename):
    """Imports a module from filename as a string, returns the contained Assistant object"""

    agent_name = os.path.splitext(filename)[0]

    try:
        agent_module = import_with_3(
            agent_name, os.path.join(os.getcwd(), filename))

    except ImportError:
        agent_module = import_with_2(
            agent_name, os.path.join(os.getcwd(), filename))

    for name, obj in agent_module.__dict__.items():
        if isinstance(obj, Assistant):
            return obj
