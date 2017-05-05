from __future__ import absolute_import
import os
import sys
import logging
import json
from flask_assistant.core import Assistant
from .schema_handlers import IntentGenerator, EntityGenerator, TemplateCreator
from .api import ApiAi
from api_ai import logger
from multiprocessing import Process

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

def get_assistant():
    agent_file = sys.argv[1]
    agent_name = os.path.splitext(agent_file)[0]
    try:
        agent_module = import_with_3(agent_name, os.path.join(os.getcwd(), agent_file))

    except ImportError:
        agent_module = import_with_2(agent_name, os.path.join(os.getcwd(), agent_file))

    for name, obj in agent_module.__dict__.items():
        if isinstance(obj, Assistant):
            return obj

def gen_templates():
    assist = get_assistant()
    templates = TemplateCreator(assist)
    templates.generate()

def intents():
    api = ApiAi()
    logger.info('Getting Registered Intents...')
    intents = api.agent_intents
    for i in intents:
        logger.info(i.name)
    return intents

def entities():
    api = ApiAi()
    logger.info('Getting Registered Entities...')
    ents = api.agent_entities
    for i in ents:
        logger.info(i.name)
    return ents


def schema():
    assist = get_assistant()
    intents = IntentGenerator(assist)
    entities = EntityGenerator(assist)
    templates = TemplateCreator(assist)

    intents.generate()
    entities.generate()
    templates.generate()

def query():
    assist = get_assistant()
    p = Process(target=assist.app.run)
    p.start()

    api = ApiAi()
    while True:
        q = input('Enter query...\n')
        resp = api.post_query(q).json()
        logger.info('Matched: {}'.format(resp['result']['metadata']['intentName']))
        logger.info('Params: {}'.format(resp['result']['parameters']))
        logger.info(resp['result']['fulfillment']['speech'])


