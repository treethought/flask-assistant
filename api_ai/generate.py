import os
import json

from .schema_models import Intent
from .api_ai import ApiAi

from flask_assistant.core import _dbgdump


class SchemaHandler(object):

    def __init__(self, assist):

        self.assist = assist
        self.intents = []
        # self._dev_token = self.assist.app.config['DEV_ACCESS_TOKEN']
        self.api = ApiAi(self.assist)

    @property
    def schema_dir(self):
        d = os.path.join(self.assist.app.root_path, 'schema')
        if not os.path.isdir(d):
            os.mkdir(d)
        return d

    @property
    def intent_file(self):
        f = os.path.join(self.schema_dir, 'intents.json')
        if not os.path.isfile(f):
            open(f, 'w+').close()
        return f

    @property
    def intent_schema(self):
        with open(self.intent_file, 'r') as f:
            try:
                return json.load(f)
            except json.decoder.JSONDecodeError:
                return []

    @property
    def registered_intents_json(self):
        if self.intent_schema:
            return [i for i in self.intent_schema if i if i.get('id')]

    @property
    def registered_intent_names(self):
        return [i['name'] for i in self.intent_schema if i['id']]

    @property
    def app_intents(self):
        """Returns a list of Intent objects created from the assistant's acion functions"""
        from_app = []
        for intent_name in self.assist._intent_action_funcs:
            intent = self.build_intent(intent_name)
            from_app.append(intent)
        return from_app

    def dump_schema(self, schema):
        print('Writing schema json to file')
        with open(self.intent_file, 'w') as f:
            json.dump(schema, f, indent=4)

    def build_intent(self, intent_name):
        """Builds an Intent object of the given name"""
        # TODO: add actions and contexts
        # dummy func to fill in action for now
        new_intent = Intent(intent_name)
        new_intent.add_action('{}-action'.format(intent_name))
        return new_intent

    def push_intent(self, intent):
        """Registers or updates an intent and returns the intent_json with an ID"""
        if intent.id:
            print('Updating {} intent'.format(intent.name))
            self.update(intent)
        else:
            print('Registering {} intent'.format(intent.name))
            intent = self.register(intent)
        return intent

    def register(self, intent):
        """Registers a new intent and returns the Intent object with an ID"""
        response = self.api.post_intent(intent.serialize)
        print(response)
        if response['status']['code'] == 200:
            intent.id = response['id']
        return intent

    def update(self, intent):
        response = self.api.put_intent(intent.id, intent.serialize)
        print(response)
        if response['status']['code'] == 200:
            return response

    def grab_id(self, intent_name):
        if self.registered_intents_json:
            for intent in self.registered_intents_json:
                if intent['name'] == intent_name:
                    return intent['id']

    def generate(self):
        print('Generating schema...')
        schema = []
        for intent in self.app_intents:
            intent.id = self.grab_id(intent.name)
            intent = self.push_intent(intent)
            schema.append(intent.__dict__)
        self.dump_schema(schema)

