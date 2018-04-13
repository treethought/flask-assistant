import os
import inspect
import json
from ruamel import yaml

from .models import Intent, Entity




class SchemaHandler(object):

    def __init__(self, assist, object_type=None):

        self.assist = assist
        self.intents = []
        self.api = assist.api
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
            except ValueError as e: # python2
                return []
            except json.decoder.JSONDecodeError: # python3
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

    def template_file(self, template_type):
        file_name = '{}.yaml'.format(template_type)
        f = os.path.join(self.template_dir, file_name)
        if not os.path.isfile(f):
            open(f, 'w+').close()
        return f

    @property
    def user_says_template(self):
        return self.template_file('user_says')

    @property
    def entity_template(self):
        return self.template_file('entities')


    def load_yaml(self, template_file):
        with open(template_file) as f:
            try:
                return yaml.safe_load(f)
            except yaml.YAMLError as e:
                print(e)
                return []

    def user_says_yaml(self):
        return self.load_yaml(self.user_says_template)

    def entity_yaml(self):
        return self.load_yaml(self.entity_template)



    def grab_id(self, obj_name):
        if self.registered:
            for obj in self.registered:
                if obj['name'] == obj_name:
                    return obj['id']


class IntentGenerator(SchemaHandler):

    def __init__(self, assist):
        super(IntentGenerator, self).__init__(assist, object_type='intents')


    @property
    def app_intents(self):
        """Returns a list of Intent objects created from the assistant's acion functions"""
        from_app = []
        for intent_name in self.assist._intent_action_funcs:
            intent = self.build_intent(intent_name)
            from_app.append(intent)
        return from_app

    def build_intent(self, intent_name):
        """Builds an Intent object of the given name"""
        # TODO: contexts
        is_fallback = self.assist._intent_fallbacks[intent_name]
        contexts = self.assist._required_contexts[intent_name]
        events = self.assist._intent_events[intent_name]
        new_intent = Intent(intent_name, fallback_intent=is_fallback, contexts=contexts, events=events)
        self.build_action(new_intent)
        self.build_user_says(new_intent)  # TODO
        return new_intent


    def build_action(self, intent):
        action_name = self.assist._intent_action_funcs[intent.name][0].__name__
        params = self.parse_params(intent.name)
        intent.add_action(action_name, parameters=params)

    def parse_params(self, intent_name):
        """Parses params from an intent's action decorator and view function.

        Returns a list of parameter field dicts to be included in the intent object's response field.
        """

        params = []
        action_func = self.assist._intent_action_funcs[intent_name][0]
        argspec = inspect.getargspec(action_func)
        param_entity_map = self.assist._intent_mappings.get(intent_name)

        args, defaults = argspec.args, argspec.defaults
        default_map = {}
        if defaults:
            default_map = dict(zip(args[-len(defaults):], defaults))

        # import ipdb; ipdb.set_trace()
        for arg in args:
            param_info = {}

            param_entity = param_entity_map.get(arg, arg)
            param_name = param_entity.replace('sys.', '')
            # param_name = arg

            param_info['name'] = param_name
            param_info['value'] = '$' + param_name
            param_info['dataType'] = '@' + param_entity
            param_info['prompts'] = []  # TODO: fill in provided prompts
            param_info['required'] = arg not in default_map
            param_info['isList'] = isinstance(default_map.get(arg), list)
            if param_info['isList']:
                param_info['defaultValue'] = ''
            else:
                param_info['defaultValue'] = default_map.get(arg, '')

            params.append(param_info)
        return params

    def get_synonyms(self, annotation, entity):
        raw_temp = self.entity_yaml()
        for temp_dict in [d for d in raw_temp if d == entity]:
            for entry in raw_temp.get(temp_dict):
                if isinstance(entry, dict):
                    for a, s in entry.items():
                        if a == annotation:
                            for synonym in s:
                                yield(synonym)

    def build_user_says(self, intent):
        raw = self.user_says_yaml()
        intent_data = raw.get(intent.name)

        if intent_data:
            phrases = intent_data.get('UserSays', [])
            annotations = intent_data.get('Annotations', [])
            events = intent_data.get('Events', [])
            mapping = {}
            for a in [a for a in annotations if a]:
                for annotation, entity in a.items():
                    mapping.update({str(annotation):str(entity)})
                    for synonym in self.get_synonyms(annotation, entity):
                        mapping.update({str(synonym):str(entity)})

            for phrase in [p for p in phrases if p]:
                if phrase != '':
                    intent.add_example(phrase, templ_entity_map=mapping)

            for event in [e for e in events if e]:
                intent.add_event(event)


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
        print()
        if response['status']['code'] == 200:
            intent.id = response['id']
        elif response['status']['code'] == 409: # intent already exists
            intent.id = next(i.id for i in self.api.agent_intents if i.name == intent.name)
            self.update(intent)
        return intent

    def update(self, intent):
        response = self.api.put_intent(intent.id, intent.serialize)
        print(response)
        print()
        if response['status']['code'] == 200:
            return response

    def generate(self):
        print('Generating intent schema...')
        schema = []
        for intent in self.app_intents:
            intent.id = self.grab_id(intent.name)
            intent = self.push_intent(intent)
            schema.append(intent.__dict__)
        self.dump_schema(schema)


class EntityGenerator(SchemaHandler):

    def __init__(self, assist):
        super(EntityGenerator, self).__init__(assist, object_type='entities')

    def build_entities(self):
        raw_temp = self.entity_yaml()

        for entity_name in raw_temp:
            e = Entity(entity_name)
            self.build_entries(e, raw_temp)
            yield e

    def build_entries(self, entity, temp_dict):
        entries = temp_dict.get(entity.name, [])
        for entry in entries:
            if isinstance(entry, dict):  # mapping
                (value, synyms), = entry.items()
            else:  # enum/composite
                entity.isEnum = True
                value = entry
                synyms = [entry]
            entity.add_entry(value, synyms)

    def register(self, entity):
        """Registers a new entity and returns the entity object with an ID"""
        response = self.api.post_entity(entity.serialize)
        print(response)
        print()
        if response['status']['code'] == 200:
            entity.id = response['id']
        if response['status']['code'] == 409: # entity already exists
            entity.id = next(i.id for i in self.api.agent_entities if i.name == entity.name)
            self.update(entity)
        return entity

    def update(self, entity):
        response = self.api.put_entity(entity.id, entity.serialize)
        print(response)
        print()
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



class TemplateCreator(SchemaHandler):

    def __init__(self, assist):
        super(TemplateCreator, self).__init__(assist)

        self.assist = assist

    def generate(self):
        if not self.user_says_yaml():
            self.create_user_says_skeleton()
        if not self.entity_yaml():
            self.create_entity_skeleton()

    def get_or_create_dir(self, dir_name):
        try:
            root = self.assist.app.root_path
        except AttributeError: # for blueprints
            root = self.assist.blueprint.root_path

        d = os.path.join(root, dir_name)

        if not os.path.isdir(d):
            os.mkdir(d)
        return d

    @property
    def template_dir(self):
        return self.get_or_create_dir('templates')

    @property
    def user_says_exists(self):
        return self._user_says_exists


    def parse_annotations_from_action_mappings(self, intent_name):
        annotations = []
        entity_map = self.assist._intent_mappings.get(intent_name, {})
        for param in entity_map:
            annotations.append({param: entity_map[param]})
        return annotations

    def create(self, user_says=True, entities=True):
        if user_says:
            self.create_user_says_skeleton()
        if entities:
            self.create_entity_skeleton()


    def create_user_says_skeleton(self):
        template = os.path.join(self.template_dir, 'user_says.yaml')

        skeleton = {}
        for intent in self.assist._intent_action_funcs:
            # print(type(intent))
            entity_map_from_action = self.assist._intent_mappings.get(intent, {})

            d = yaml.compat.ordereddict()
            d['UserSays'] = [None, None]
            d['Annotations'] = [None, None]
            d['Events'] = [None]

            # d['Annotations'] = self.parse_annotations_from_action_mappings(intent)

            data = yaml.comments.CommentedMap(d)  # to preserve order w/o tags
            skeleton[intent] = data

        with open(template, 'a') as f:
            f.write('# Template for defining UserSays examples\n\n')
            f.write('# give-color-intent:\n\n')
            f.write('#  UserSays:\n')
            f.write('#    - My color is blue\n')
            f.write('#    - red is my favorite color\n\n')
            f.write('#  Annotations:\n')
            f.write('#    - blue: sys.color     # maps param value -> entity\n')
            f.write('#    - red: sys.color\n\n')
            f.write('#  Events:\n')
            f.write('#    - event1              # adds a triggerable event named \'event1\' to the intent\n\n\n\n')
            # f.write(header)
            yaml.dump(skeleton, f, default_flow_style=False, Dumper=yaml.RoundTripDumper)


    def create_entity_skeleton(self):
        print('Creating Template for Entities')
        template = os.path.join(self.template_dir, 'entities.yaml')
        message = """# Template file for entities\n\n"""

        skeleton = {}
        for intent in self.assist._intent_action_funcs:
            entity_map = self.assist._intent_mappings.get(intent)
            action_func = self.assist._intent_action_funcs[intent][0]
            args = inspect.getargspec(action_func).args

            # dont add API 'sys' entities to the template
            if entity_map:
                args = [a for a in args if 'sys.' not in entity_map.get(a, [])]

            for param in [p for p in args if p not in skeleton]:
                skeleton[param] = [None, None]

        with open(template, 'w') as f:
            f.write(message)
            f.write('#Format as below\n\n')
            f.write("# entity_name:\n")
            f.write("#  - entry1: list of synonyms \n")
            f.write("#  - entry2: list of synonyms \n\n")
            f.write("#For example:\n\n")
            f.write("# drink:\n")
            f.write("#  - water: ['aqua', 'h20'] \n")
            f.write("#  - coffee: ['joe', 'caffeine', 'espresso', 'late'] \n")
            f.write("#  - soda: ['pop', 'coke']\n\n\n\n")
            yaml.dump(skeleton, f, default_flow_style=False, Dumper=yaml.RoundTripDumper)

