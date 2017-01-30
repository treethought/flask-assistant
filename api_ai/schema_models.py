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


class Entity():
    """docstring for Entity"""

    def __init__(self, name):
        self.name = name
        self.entries = []

    def add_entry(self, value, synonyms=[]):
        # import ipdb; ipdb.set_trace()
        entry = {'value': value, 'synonyms': synonyms}
        self.entries.append(entry)
        # self.entries[value] = synonyms

    def add_synonyms(self, entry, synonyms):
        self.entries[entry].extend(synonyms)

    @property
    def serialize(self):
        return json.dumps(self.__dict__)

    def __repr__(self):
        return '@' + self.name


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

    def __init__(self, phrase, mapping):
        super(UserDefinedExample, self).__init__(phrase, user_defined=True)
        # import ipdb; ipdb.set_trace()
        # self.phrase = phrase
        self.mapping = mapping

        self.parse_phrase()

    def parse_phrase(self):
        # import ipdb; ipdb.set_trace()
        annotated = {}
        sub_phrase = ''

        for word in self.text.split():
            if word in self.mapping:
                'mapping triggered for {}'.format(word)
                self.data.append({'text': sub_phrase})  # add non-annotated, then deal with annotation
                sub_phrase = ''
                self.annotate(word)

            else:
                sub_phrase += '{} '.format(word)

        if sub_phrase:
            self.data.append({'text': sub_phrase})

    def annotate(self, word):
        annotation = {}
        annotation['text'] = word
        annotation['meta'] = '@' + self.mapping[word]
        annotation['alias'] = self.mapping[word]
        annotation['userDefined'] = True
        self.data.append(annotation)


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


    def add_example(self, phrase, mapping=None):  # TODO
        if mapping:
            example = UserDefinedExample(phrase, mapping)
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

    @property
    def serialize(self):
        return json.dumps(self.__dict__)

    def update(self, intent_json):
        self.__dict__.update(json.loads(intent_json))
        return self._update
