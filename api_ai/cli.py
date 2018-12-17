from __future__ import absolute_import
import sys
import logging
from flask_assistant.utils import get_assistant
from .schema_handlers import IntentGenerator, EntityGenerator, TemplateCreator
from .api import ApiAi
from . import logger
from multiprocessing import Process

logger.setLevel(logging.INFO)

api = ApiAi()

raise DeprecationWarning(
    "Schema generation and management is not yet available for Dialogflow V2, please define intents and entities in the Dialogflow console"
)


def file_from_args():
    try:
        return sys.argv[1]
    except IndexError:
        raise IndexError("Please provide the file containing the Assistant object")


def gen_templates():
    filename = file_from_args()
    assist = get_assistant(filename)
    templates = TemplateCreator(assist)
    templates.generate()


def intents():
    logger.info("Getting Registered Intents...")
    filename = file_from_args()
    assist = get_assistant(filename)
    intents = assist.api.agent_intents
    for i in intents:
        logger.info(i.name)
    return intents


def entities():
    logger.info("Getting Registered Entities...")
    filename = file_from_args()
    assist = get_assistant(filename)
    ents = assist.api.agent_entities
    for i in ents:
        logger.info(i.name)
    return ents


def schema():
    filename = file_from_args()
    assist = get_assistant(filename)
    intents = IntentGenerator(assist)
    entities = EntityGenerator(assist)
    templates = TemplateCreator(assist)

    templates.generate()
    intents.generate()
    entities.generate()


def check():
    filename = file_from_args()
    assist = get_assistant(filename)
    # reg_total = len(assist.api.agent_intents)
    # map_total = len(assist._intent_action_funcs)
    reg_names = [i.name for i in assist.api.agent_intents]
    map_names = [i for i in assist._intent_action_funcs.keys()]
    extra_reg = set(reg_names) - set(map_names)
    extra_map = set(map_names) - set(reg_names)

    if extra_reg != set():
        print(
            "\nThe following Intents are registered but not mapped to an action function:"
        )
        print(extra_reg)
        print()
    else:
        print("\n All registered intents are mapped\n")

    if extra_map != set():
        print(
            "\nThe Following Intents are mapped to an action fucntion, but not registered: "
        )
        print(extra_map)
        print()
    else:
        print("\n All mapped intents are regitsered\n")

    print("Registered Entities:")
    print([i.name for i in assist.api.agent_entities])


def query():
    filename = file_from_args()
    assist = get_assistant(filename)
    p = Process(target=assist.app.run)
    p.start()

    while True:
        q = input("Enter query...\n")
        resp = assist.api.post_query(q).json()
        try:
            print("Matched: {}".format(resp["result"]["metadata"]["intentName"]))
            print("Params: {}".format(resp["result"]["parameters"]))
            print(resp["result"]["fulfillment"]["speech"])

        except KeyError:
            logger.error("Error:")
            logger.error(resp["status"])
