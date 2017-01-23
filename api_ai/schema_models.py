import json


class _Field(dict):

    def __init__(self, request_json={}):
        super(_Field, self).__init__(request_json)
        for key, value in request_json.items():
            if isinstance(value, dict):
                value = _Field(value)
            self[key] = value

    def __getattr__(self, attr):
        return self.get(attr)

    def __setattr__(self, key, value):
        self.__setitem__(key, value)


class Entity(_Field):
    """docstring for Entity"""

    def __init__(self, name, entries=[]):
        super(Entity, self).__init__()
        self.name = name
        self.entries = entries

    def add_entry(self, value, synonyms=[]):
        self.entries[value] = synonyms

    def add_synonyms(self, entry, synonyms):
        self.entries[entry].extend(synonyms)

    def __repr__(self):
        return '@' + self.name


class Example(object):
    """docstring for Example"""

    def __init__(self, phrase, entity_map={}):
        super(Example, self).__init__(isTemplate=False)
        self._phrase = phrase
        self._entity_map = entity_map

        if not _entity_map:
            auto_annotate = {
                'text': self._phrase,
                'userDefined': False
            }
            self.data.append(auto_annotate)

        else:
            self.parse_speech()

    @property
    def split_speech(self):
        return self._phrase.split(' ')

    def sub_phrase_obj(self, text):
        return {
            'text': text,
        }

    def parse_speech(self):
        annotated = {}
        sub_phrase = ''
        for word in self.split_speech:
            sub_phrase += '{} '.format(word)

            if word in entity_map:
                annotated['text'] = word
                annotated['meta'] = '@' + entity_map[word]
                annotated['alias'] = entity_map[word]


class Intent():
    """Represents an Intent object within the API.AI REST APi.

    Intents are created internally using an Assistant app's action decorated view functions
    These objects provide the JSON schema for registering, updating, and removing intents in
    the API.AI develoepr console via JSON requests.

    Attributes:
        auto (bool): True if Mahcine Learning is on
        contexts (list): List of input contexts required to trigger intent
        fallback_intent (bool): True if intent is a fallback intent
        name (str): Name of the intent
        priority (int): Intent priority
        templates (list): Templates that this intent will match
        user_says (list): list of examples or template objects
        webhookForSlotFilling (bool): enable webhook handling of intent required parameters
        webhookUsed (bool): True if webhook enabled for intent (True when using flask-assitant)
    """

    def __init__(self, name, auto=True, contexts=[],
                 templates=[], user_says=[], responses=[], priority=500000,
                 slot_filling=True, fallback_intent=False, events=[]):

        self.name = name
        self.auto = auto
        self.contexts = contexts
        self.templates = templates
        self.userSays = user_says
        self.responses = responses
        self.priority = priority
        self.fallbackIntent = fallback_intent
        self.webhookUsed = True
        self.webhookForSlotFilling = slot_filling
        self.events = events
        self.id = None


    def registered(self):
        if self.id:
            return True

    def add_user_example(self):
        pass

    def add_action(self, action_name):
        self.responses = [{
            'action': action_name,
            'resetContexts': False,
            'affectedContexts': [],  # TODO: register context outs
            'parameters': [],  # TODO: register parameters from action_funcs
            'messages': []  # TODO: possibly register action responses to call from intent object directly
        }]
        # self.responses.append(new_response)
    

    @property
    def serialize(self):
        return json.dumps(self.__dict__)

    def update(self, intent_json):
        self.__dict__.update(json.loads(intent_json))
        return self._update
    
