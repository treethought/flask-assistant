import os
import requests
import datetime



class ApiAi(object):
    """Interface for making and recieving API-AI requests.

    Use the developer access token for managing entities and intents and the client access token for making queries.

    """

    def __init__(self, assistant):

        self.assist = assistant
        self._dev_token = self.assist.app.config['DEV_ACCESS_TOKEN']
        self.versioning = '20161213'
        self.base_url = 'https://api.api.ai/v1/'

    @property
    def foo(self):
        return self._foo

    def _endpoint_uri(self, endpoint):
        return

    @property
    def _intent_uri(self, intent_id=''):
        if intent_id != '':
            intent_id = '/' + intent_id
        return '{}intents{}?v={}'.format(self.base_url, intent_id, self.versioning)

    @property
    def _dev_header(self):
        return {'Authorization': 'Bearer {}'.format(self._dev_token)}

    def _get_response(self, endpoint):
        response = requests.get(endpoint, headers=self._dev_header)
        response.raise_for_status
        return response.json()

    @property
    def get_agent_intents(self):
        """Returns a list of intent json objects"""
        endpoint = self._intent_uri
        intents = [_Field(i) for i in self._get_response(endpoint)]
        return intents

    def get_intent(intent_id):
        """Returns the intent object with the given intent_id"""
        endpoint = self._intent_uri(intent_id=intent_id)
        return self._get_response()


class _Field(dict):

    def __init__(self, request_json={}):
        super(_Field, self).__init__(request_json)
        for key, value in request_json.items():
            if isinstance(value, dict):
                value = _Field(value)
            self[key] = value

    def __getattr__(self, attr):
        # converts timestamp str to datetime.datetime object
        if 'timestamp' in attr:
            return aniso8601.parse_datetime(self.get(attr))
        return self.get(attr)

    def __setattr__(self, key, value):
        self.__setitem__(key, value)
