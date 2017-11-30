# coding: utf8

import json
import re

class Entity():
    """docstring for Entity"""

    def __init__(self, name=None, entity_json=None):

        if name and not entity_json:
            self.name = name
            self.entries = []
            self.isEnum = None
            self.id = None

        elif entity_json:
            self.update(entity_json)

        else:
            raise TypeError('Must provide a "name" argument if no json given')

    def add_entry(self, value, synonyms=[]):
        if self.isEnum:
            entry = {'value': value, 'synonyms': value}
        entry = {'value': value, 'synonyms': synonyms}
        self.entries.append(entry)


    def add_synonyms(self, entry, synonyms):
        self.entries[entry].extend(synonyms)

    @property
    def serialize(self):
        return json.dumps(self.__dict__)

    def __repr__(self):
        return '@' + self.name

    def update(self, entity_json):
        try:
            self.__dict__.update(entity_json)
        except TypeError:
            self.__dict__.update(json.loads(entity_json))


class Intent():
    """Represents an Intent object within the API.AI REST APi.

    Intents are created internally using an Assistant app's action decorated view functions
    These objects provide the JSON schema for registering, updating, and removing intents in
    the API.AI develoepr console via JSON requests.
    """

    def __init__(self, name=None, priority=500000, fallback_intent=False, contexts=None, events=None, intent_json=None):

        if name and not intent_json:
            self.name = name
            self.auto = True
            self.contexts = contexts or []
            self.templates = []
            self.userSays = []
            self.responses = []
            self.priority = priority
            self.fallbackIntent = fallback_intent
            self.webhookUsed = True
            self.webhookForSlotFilling = True
            self.events = Intent._build_events(events)
            self.id = None

        elif intent_json:
            self.update(intent_json)

        else:
            raise TypeError('Must provide a "name" argument if no json given')

    @staticmethod
    def _build_events(events):
        return [] if events is None else [{'name': event} for event in events]

    def __repr__(self):
        return "<Intent: {}>".format(self.name)

    def registered(self):
        if self.id:
            return True


    def add_example(self, phrase, templ_entity_map=None):  # TODO
        if templ_entity_map:
            example = UserDefinedExample(phrase, templ_entity_map)
        else:
            example = AutoAnnotedExamle(phrase)

        self.userSays.append(example.serialize)

    def add_action(self, action_name, parameters=[]):
        self.responses = [{
            'action': action_name,
            'resetContexts': False,
            'affectedContexts': [],  # TODO: register context outs
            'parameters': parameters,
            'messages': []  # TODO: possibly register action responses to call from intent object directly
        }]
        # self.responses.append(new_response)
    
    def add_event(self, event_name):
        self.events.append({'name': event_name})

    @property
    def serialize(self):
        return json.dumps(self.__dict__)

    def update(self, intent_json):
        try:
            self.__dict__.update(intent_json)
        except TypeError:
            self.__dict__.update(json.loads(intent_json))



class ExampleBase(object):
    """docstring for ExampleBase"""

    def __init__(self, phrase, user_defined=False, isTemplate=False):

        self.text = phrase
        self.userDefined = user_defined
        self.isTemplate = isTemplate
        self.data = []

    @property
    def serialize(self):
        return {
            'data': self.data,
            'isTemplate': self.isTemplate,
            'count': 0
        }


class AutoAnnotedExamle(ExampleBase):

    def __init__(self, phrase):
        super(AutoAnnotedExamle, self).__init__(phrase)
        self.text = phrase
        self.data.append({'text': self.text, 'userDefined': False})


class UserDefinedExample(ExampleBase):

    def __init__(self, phrase, entity_map):
        super(UserDefinedExample, self).__init__(phrase, user_defined=True)
        # import ipdb; ipdb.set_trace()
        self.entity_map = entity_map

        self._parse_phrase(self.text)

    def _parse_phrase(self, sub_phrase):
        if not sub_phrase:
            return

        for value in self.entity_map:
            re_value = r".\b{}\b".format(value[1:]) if value.startswith(('$', '¥', '￥', '€', '£')) else r"\b{}\b".format(value)
            if re.search(re_value, sub_phrase):
                parts = sub_phrase.split(value, 1)
                self._parse_phrase(parts[0])
                self._annotate_params(value)
                self._parse_phrase(parts[1])
                return

        self.data.append({'text': sub_phrase})

    def _annotate_params(self, word):
        """Annotates a given word for the UserSays data field of an Intent object.

        Annotations are created using the entity map within the user_says.yaml template.
        """
        annotation = {}
        annotation['text'] = word
        annotation['meta'] = '@' + self.entity_map[word]
        annotation['alias'] = self.entity_map[word].replace('sys.', '')
        annotation['userDefined'] = True
        self.data.append(annotation)

