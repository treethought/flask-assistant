
SYSTEM_INTENT_TYPES = {
    'actions.intent.TEXT': None,
    'actions.intent.OPTION': 'type.googleapis.com/google.actions.v2.OptionValueSpec'
}

class _RichResponse(object):

    def __init__(self):
        self.items = []
        self.suggestions = []
        self.link_out = {}

        self._data = {}

    def _load_data(self):
        self._data['items'] = self.items
        if self.suggestions:
            self._data['suggestions'] = self.suggestions
        if self.link_out:
            self._data['linkOutSuggestion'] = self.link_out
        return self._data

    def add_simple_response_item(self, speech, display_text):
        """Builds a simple response containing speech or text to show the user

        Every _RichResponse requires this type of response as the first item

        This object does not include the ssml field found in the Actions API
        because DialogFlowformats the ssml based off the value of data.google.isSsml
        """

        simple = {'textToSpeech': speech, 'displayText': display_text}
        payload = {'simpleResponse': simple}
        self.items.append(payload)

    def add_basic_card(self, card_obj):
        card = {'basicCard': card_obj._load_data()}
        self.items.append(card)

    def add_suggestion(self, title):
        """Provides a suggestion chip that the user can tap to quickly post a reply to the conversation

            If used in a FinalResponse, they will be ignored.
        """
        suggestion = {'title': title}
        self.suggestions.append(suggestion)

    def add_link_out(self, dest, url):
        """An additional suggestion chip that can link out to the associated app or site."""
        if len(self.link_out) > 0:
            raise ValueError('Only one linkOutSuggestion may be given')

        payload = {
            'destinationName': dest,
            'url': url
        }
        self.link_out = payload



class _SystemIntent(object):
    """Defines expected (Actions) intent along with extra config data

        This represents the type of data to be received from the user.

        To have the Google Assistant just return the raw user input,
        the app should ask for the actions.intent.TEXT intent.

        Possible intents:
            TEXT
            OPTION
            CONFIRMATION
            TRANSACTION_REQUIREMENTS_CHECK
            DELIVERY_ADDRESS
            TRANSACTION_DECISION

        https://developers.google.com/actions/components/intents
        https://developers.google.com/actions/reference/rest/Shared.Types/AppResponse#ExpectedIntent
    """

    def __init__(self, intent='text'):

        self.intent = 'actions.intent.{}'.format(intent.upper())

        self.value_spec_type = SYSTEM_INTENT_TYPES[self.intent]
        self.input_value_data = {}

    def set_value_data(self, value_spec):
        """Attach the conifguration data required by one of the possible intents

        actions.intent.OPTION requires a SimpleSelect, ListSelect, or CarouselSelect value spec object

        Arguments:
            value_spec {obj} -- COnfiguration data for the built-in actions intent
        """

        self.input_value_data['@type'] = self.value_spec_type

        # now just attach the valuespec payload (list/carousel)
        value_spec_data = value_spec._load_data()
        self.input_value_data.update(value_spec_data)

    def _load_data(self):
        if self.input_value_data is None:
            return {'intent': self.intent}
        return {'intent': self.intent, 'data': self.input_value_data}








