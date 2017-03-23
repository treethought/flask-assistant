import json

class Entity():
    """docstring for Entity"""

    def __init__(self, name):
        self.name = name
        self.entries = []
        self.isEnum = None

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




class Intent():
    """Represents an Intent object within the API.AI REST APi.

    Intents are created internally using an Assistant app's action decorated view functions
    These objects provide the JSON schema for registering, updating, and removing intents in
    the API.AI develoepr console via JSON requests.
    """

    def __init__(self, name, priority=500000, fallback_intent=False):

        self.name = name
        self.auto = True
        self.contexts = []
        self.templates = []
        self.userSays = []
        self.responses = []
        self.priority = priority
        self.fallbackIntent = fallback_intent
        self.webhookUsed = True
        self.webhookForSlotFilling = True
        self.events = []
        self.id = None

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

    @property
    def serialize(self):
        return json.dumps(self.__dict__)

    def update(self, intent_json):
        self.__dict__.update(json.loads(intent_json))
        return self._update


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

        self.parse_phrase()

    def parse_phrase(self):
        # import ipdb; ipdb.set_trace()
        annotated = {}
        sub_phrase = ''

        for word in self.text.split():
            if word in self.entity_map:
                self.data.append({'text': sub_phrase})  # add non-annotated, then deal with annotation
                sub_phrase = ''
                self.annotate_params(word)

            else:
                sub_phrase += '{} '.format(word)

        if sub_phrase:
            self.data.append({'text': sub_phrase})

    def annotate_params(self, word):
        """Annotates a given word for the UserSays data field of an Intent object.
        
        Annotations are created using the entity map within the user_says.yaml template.
        """
        annotation = {}
        annotation['text'] = word
        annotation['meta'] = '@' + self.entity_map[word]
        annotation['alias'] = self.entity_map[word].replace('sys.', '')
        annotation['userDefined'] = True
        self.data.append(annotation)

