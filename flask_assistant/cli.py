import os
import sys
import importlib

from flask_assistant.core import Assistant
from flask_assistant.api_ai.generate import SchemaHandler


def main():
    agent_file = sys.argv[1]
    agent_name = os.path.splitext(agent_file)[0]
    import ipdb
    agent_module = importlib.import_module(agent_name, os.getcwd())

    for name, obj in agent_module.__dict__.items():
        if isinstance(obj, Assistant):
            assist = obj
            schema = SchemaHandler(assist)
            schema.generate()
            print('generating')
            break

if __name__ == '__main__':
    main()
