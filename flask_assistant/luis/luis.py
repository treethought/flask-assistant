from flask import json, request as flask_request
import requests
import os

from flask_assistant.core import Assistant
from secret import *

from pprint import pprint


LUIS_APP_ID = os.getenv('LUIS_APP_ID')
LUIS_ENDPOINT_KEY =  os.getenv('LUIS_ENDPOINT_KEY')

LUIS_ENDPOINT = 'https://westus.api.cognitive.microsoft.com/luis/v2.0/apps/{}?subscription-key={}'.format(LUIS_APP_ID, LUIS_ENDPOINT_KEY)

class Bot(Assistant):
    """The Bot object serves as the interface for manning requests from the
        
        Central Interface for for handling communication between Microsoft Bot Framework and Luis applications.

        The Bot object receives requests from the Bot Framework pertaining to a user's request.
        The incoming request is used to query our LUIS application, and match the LUIS intent to the proper view function.

     """
    def __init__(self, app, route='/'):
        super().__init__(app, route)


    def _dump_report(self):
        report = {
            'User Message': self.request,
            'LUIS result': self.result,
            }
        pprint(report, indent=3)

    def _flask_assitant_view_func(self, *args, **kwargs):
        self.request = self._bot_framework_request(verify=False)
        self.result = self._query_luis(self.request['text'])
        self._dump_report()


        self.intent = self.result['topScoringIntent']['intent']
        self.entities = self.result['entities']
     

        view_func = self._intent_action_funcs[self.intent]
        result = self._map_intent_to_view_func(view_func)

    def _map_intent_to_view_func(self, view_func):
        arg_names = self._func_args(view_func)
        arg_values = self._map_params_to_view_args(arg_names)
        return partial(view_func, *arg_values)

    def _map_params_to_view_args(self, arg_names): # TODO map to correct name
        arg_values = {}
        intent_map = self._intent_mappings.get(self.intent)
        

        for arg_name in arg_names:
            arg_values[arg_name] = [] # may recieve multiple entities of the same type
            mapped_name = intent_map.get(arg_name, arg_name)

            for entity in self.entities:
                if entity['type'] == mapped_name:
                    value = entity['entity']
                    arg_values[arg_name].append(value)

        return arg_values




    def _bot_framework_request(self, verify=True):
        raw_body = flask_request.data
        return json.loads(raw_body)

    def _query_luis(self, message, *args, **kwargs):
        query = LUIS_ENDPOINT + '&q={}&timezoneOffset=0.0&verbose=true'.format(message)
        result = requests.get(query).text
        return json.loads(result)


