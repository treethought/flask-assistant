import os
import inspect
import json
from ruamel import yaml

from api_ai.models import Intent, Entity
from api_ai.api_ai import ApiAi

from flask_assistant.core import _dbgdump


class SchemaHandler(object):

    def __init__(self, assist, object_type=None):

        self.assist = assist
        self.intents = []
        self.api = ApiAi(self.assist)
        self.object_type = object_type

    # File set up

    def get_or_create_dir(self, dir_name):
        d = os.path.join(self.assist.app.root_path, dir_name)
        if not os.path.isdir(d):
            os.mkdir(d)
        return d

    @property
    def schema_dir(self):
        return self.get_or_create_dir('schema')

    @property
    def json_file(self):
        file_name = '{}.json'.format(self.object_type)
        f = os.path.join(self.schema_dir, file_name)
        if not os.path.isfile(f):
            open(f, 'w+').close()
        return f

    @property
    def saved_schema(self):
        with open(self.json_file, 'r') as f:
            try:
                return json.load(f)
            except json.decoder.JSONDecodeError:
                return []

    @property
    def registered(self):
        if self.saved_schema:
            return [i for i in self.saved_schema if i if i.get('id')]

    def dump_schema(self, schema):
        print('Writing schema json to file')
        with open(self.json_file, 'w') as f:
            json.dump(schema, f, indent=4)

    # templates
    @property
    def template_dir(self):
        return self.get_or_create_dir('templates')

    @property
    def template_file(self):
        file_name = '{}.yaml'.format(self.object_type)
        f = os.path.join(self.template_dir, file_name)
        if not os.path.isfile(f):
            open(f, 'w+').close()
        return f

    def load_yaml(self):
        with open(self.template_file) as f:
            try:
                return yaml.safe_load(f)
            except yaml.YAMLError as e:
                print(e)
                return []

    def grab_id(self, obj_name):
        if self.registered:
            for obj in self.registered:
                if obj['name'] == obj_name:
                    return obj['id']


class IntentGenerator(SchemaHandler):

    def __init__(self, assist):
        super(IntentGenerator, self).__init__(assist, object_type='intents')

        self.user_says_handler = SchemaHandler(self.assist, object_type='user_says')

        if not self.user_says_handler.load_yaml():
            self.create_user_says_skeleton()

    def create_user_says_skeleton(self):
        template = os.path.join(self.template_dir, 'user_says.yaml')

        skeleton = {}
        for intent in self.assist._intent_action_funcs:
            d = yaml.compat.ordereddict()
            d['UserSays'] = ['', '']
            d['Annotations'] = [{'param': 'entity'}, {}, {}]
            data = yaml.comments.CommentedMap(d)  # to preserve order w/o tags
            skeleton[intent] = data

        with open(template, 'a') as f:
            f.write('# Template for defining UserSays examples\n\n')
            yaml.dump(skeleton, f, default_flow_style=False, Dumper=yaml.RoundTripDumper)


    @property
    def app_intents(self):
        """Returns a list of Intent objects created from the assistant's acion functions"""
        from_app = []
        for intent_name in self.assist._intent_action_funcs:
            intent = self.build_intent(intent_name)
            from_app.append(intent)
        return from_app

    def build_action(self, intent):
        action = self.assist._intent_action_funcs[intent.name][0].__name__
        params = self.parse_params(intent.name)
        intent.add_action(action, parameters=params)

    def build_user_says(self, intent):
        raw = self.user_says_handler.load_yaml()
        intent_data = raw.get(intent.name)
        
        if intent_data:
            phrases = intent_data.get('UserSays', [])
            annotations = intent_data.get('Annotations', [])
            mapping = {}
            for a in annotations:
                mapping.update(a)

            for phrase in phrases:
                if phrase != '':
                    intent.add_example(phrase, mapping=mapping)


    def build_intent(self, intent_name):
        """Builds an Intent object of the given name"""
        # TODO: contexts
        new_intent = Intent(intent_name)
        self.build_action(new_intent)
        self.build_user_says(new_intent)  # TODO
        return new_intent

    def parse_params(self, intent_name):
        params = []
        action_func = self.assist._intent_action_funcs[intent_name][0]
        argspec = inspect.getargspec(action_func)

        args, defaults = argspec.args, argspec.defaults
        default_map = {}
        if defaults:
            default_map = dict(zip(args[-len(defaults):], defaults))

        for arg in args:
            param_field = {
                'name': arg,
                'value': '$' + arg,
                'defaultValue': default_map.get(arg, ''),
                'required': arg not in default_map,
                'dataType': '@' + arg,
                'isList': False
            }
            params.append(param_field)
        return params

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

    def generate(self):
        print('Generating intent schema...')
        schema = []
        for intent in self.app_intents:
            print(intent)
            intent.id = self.grab_id(intent.name)
            intent = self.push_intent(intent)
            schema.append(intent.__dict__)
        self.dump_schema(schema)


class EntityGenerator(SchemaHandler):

    def __init__(self, assist):
        super(EntityGenerator, self).__init__(assist, object_type='entities')

        if not self.load_yaml():
            self.create_entity_skeleton()

    def create_entity_skeleton(self):
        print('Creating Template for Entities')
        template = os.path.join(self.template_dir, 'entities.yaml')
        message = """# Template file for entities\n"""

        skeleton = {}
        for intent in self.assist._intent_action_funcs:
            action_func = self.assist._intent_action_funcs[intent][0]
            args = inspect.getargspec(action_func).args
            for param in [p for p in args if p not in skeleton]:
                skeleton[param] = [{'entry1': ['list of syonyms']}, {'entry2': ['list of synonyms']}]

        with open(template, 'w') as f:
            f.write(message)
            yaml.dump(skeleton, f)

    def build_entities(self):
        raw_temp = self.load_yaml()

        for entity_name in raw_temp:
            e = Entity(entity_name)
            self.build_entries(e, raw_temp)
            yield e

    def build_entries(self, entity, temp_dict):
        entries = temp_dict.get(entity.name, [])
        for entry in entries:
            if isinstance(entry, dict):
                (value, synyms), = entry.items()
            else:
                value = entry
                synyms = []
            entity.add_entry(value, synyms)

    def register(self, entity):
        """Registers a new entity and returns the entity object with an ID"""
        response = self.api.post_entity(entity.serialize)
        print(response)
        if response['status']['code'] == 200:
            entity.id = response['id']
        return entity

    def update(self, entity):
        response = self.api.put_entity(entity.id, entity.serialize)
        print(response)
        if response['status']['code'] == 200:
            return response

    def push_entity(self, entity):
        """Registers or updates an entity and returns the entity_json with an ID"""
        if entity.id:
            print('Updating {} entity'.format(entity.name))
            self.update(entity)
        else:
            print('Registering {} entity'.format(entity.name))
            entity = self.register(entity)
        return entity

    def generate(self):
        print('Generating entity schema...')
        schema = []
        for entity in self.build_entities():
            entity.id = self.grab_id(entity.name)
            entity = self.push_entity(entity)
            schema.append(entity.__dict__)
        self.dump_schema(schema)


