from __future__ import absolute_import
import os
import sys
import logging
from flask_assistant.core import Assistant
from .schema_handlers import IntentGenerator, EntityGenerator, TemplateCreator
from .api import ApiAi
from . import logger
from multiprocessing import Process

logger.setLevel(logging.INFO)

api = ApiAi()

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
    if len(sys.argv) < 2:
        raise KeyError('Please provide the file containing the Assistant object')
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
    logger.info('Getting Registered Intents...')
    intents = api.agent_intents
    for i in intents:
        logger.info(i.name)
    return intents


def entities():
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

    templates.generate()
    intents.generate()
    entities.generate()
    


def check():
    assist = get_assistant()
    reg_total = len(assist.api.agent_intents)
    map_total = len(assist._intent_action_funcs)
    reg_names = [i.name for i in assist.api.agent_intents]
    map_names = [i for i in assist._intent_action_funcs.keys()]
    extra_reg = set(reg_names) - set(map_names)
    extra_map = set(map_names) - set(reg_names)

    if extra_reg != set():
        print('\nThe following Intents are registered but not mapped to an action function:')
        print(extra_reg)
        print()
    else:
        print('\n All registered intents are mapped\n')

    if extra_map != set():
        print('\nThe Following Intents are mapped to an action fucntion, but not registered: ')
        print(extra_map)
        print()
    else:
        print('\n All mapped intents are regitsered\n')

    print('Registered Entities:')
    print([i.name for i in assist.api.agent_entities])


def query():
    assist = get_assistant()
    p = Process(target=assist.app.run)
    p.start()

    while True:
        q = input('Enter query...\n')
        resp = api.post_query(q).json()
        try:
            print('Matched: {}'.format(resp['result']['metadata']['intentName']))
            print('Params: {}'.format(resp['result']['parameters']))
            print(resp['result']['fulfillment']['speech'])

        except KeyError:
            logger.error('Error:')
            logger.error(resp['status'])
