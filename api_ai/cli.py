from __future__ import absolute_import
import os
import sys

from flask_assistant.core import Assistant
from .schema_handlers import IntentGenerator, EntityGenerator, TemplateCreator
from .api_ai import ApiAi
from multiprocessing import Process


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
    TemplateCreator(assist)


def schema():
    assist = get_assistant()
    intents = IntentGenerator(assist)
    entities = EntityGenerator(assist)
    template_creator = TemplateCreator(assist)

    intents.generate()
    entities.generate()

def query():
    assist = get_assistant()
    p = Process(target=assist.app.run)
    p.start()

    api = ApiAi()
    while True:
        q = input('Enter query...\n')
        resp = api.post_query(q).json()
        print('Matched: {}'.format(resp['result']['metadata']['intentName']))
        print('Params: {}'.format(resp['result']['parameters']))
        print(resp['result']['fulfillment']['speech'])


if __name__ == '__main__':
    main()
