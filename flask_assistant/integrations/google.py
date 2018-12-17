# TODO texttospeech mutually exclusive with ssml


class _GoogleIntegration():
    """Represents the data.google object of the _ApiAiResponse.

    The _GoogleIntegration object is not to be rendered as a response but rather
    to extend an existing response to be returned to Api.AI. It contains all the
    data required for communicating with Actions on Google via Api.AI.

    The data is sent to the client in the original form and is not processed by API.AI.

    Note that the contents of this class mirror the Actions API.AI webhook format,
    which closely resembles but is not identical to the Conversation webhook API.ai


    Migration guide - https://developers.google.com/actions/reference/v1/migration#apiai_webhook_protocol_changes
    Webhook Response format - https://developers.google.com/actions/apiai/webhook

    # InputPrompt.FIELDS.rich_initial_prompt
    Relavent Field for RIch Response - https://developers.google.com/actions/reference/rest/Shared.Types/AppResponse
    # ExpectedInput.FIELDS.possible_intents
    Relavent field for SystemIntent - https://developers.google.com/actions/reference/rest/Shared.Types/AppResponse

    V1 info - https://developers.google.com/actions/reference/v1/apiai-webhook

    Sample Responses - https://developers.google.com/actions/assistant/responses

    """

    def __init__(self):
        self.expect_response = True
        self.is_ssml = True
        self.speech = ''

        self.system_intent = {}
        self.rich_response = _RichResponse()
        self.final_response = {}

        self._data = {}

    def simple_response(self, speech, display_text, expect_response):
        self.speech = speech
        self.display_text = display_text
        self.expect_response = expect_response

        self.rich_response.add_simple_response_item(speech, display_text)
        expected_intent = _SystemIntent('TEXT')
        self.system_intent = expected_intent

        return self._load_data()

    def suggestion(self, title):
        self.rich_response.add_suggestion(title)
        # expected_intent = _SystemIntent('TEXT')._load_data()
        # self.system_intent = expected_intent
        return self._load_data()

    def link_out(self, dest, url):
        self.rich_response.add_link_out(dest, url)
        return self._load_data()

    def build_card(self, title=None, subtitle=None, body_text=None, img=None, btns=None, img_options=None):
        card = BasicCard(title, subtitle, body_text, img, btns, img_options)
        self.rich_response.add_basic_card(card)
        return self._load_data()

    def attach_card(self, card):
        self.rich_response.add_basic_card(card)
        return self._load_data()

    def attach_list(self, list_obj):
        expected_intent = _SystemIntent('OPTION')
        expected_intent.set_value_data(list_obj)
        self.system_intent = expected_intent
        return self._load_data()

    def _load_data(self):
        self._data['speech'] = self.speech
        self._data['expectUserResponse'] = self.expect_response
        # The ssml field in a SimpleResponse. IGNORED IN V2
        self._data['isSsml'] = True
        self._data['finalResponse'] = {}

        # optional?
        self._data['noInputPrompts'] = []

        # A RichResponse in an expectedInputs.inputPrompt.richInitialPrompt
        self._data['richResponse'] = self.rich_response._load_data()

        # replaces expectedInputs.possibleIntents
        self._data['systemIntent'] = self.system_intent._load_data()
        return self._data





SYSTEM_INTENT_TYPES = {
    'actions.intent.TEXT': None,
    'actions.intent.OPTION': 'type.googleapis.com/google.actions.v2.OptionValueSpec'
}


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
        print('*****')
        print('Setting value spec')
        self.input_value_data['@type'] = self.value_spec_type

        # now just attach the valuespec payload (list/carousel)
        value_spec_data = value_spec._load_data()
        self.input_value_data.update(value_spec_data)
        print('Value data')
        print(self.input_value_data)

    def _load_data(self):
        if self.input_value_data is None:
            return {'intent': self.intent}
        return {'intent': self.intent, 'data': self.input_value_data}



