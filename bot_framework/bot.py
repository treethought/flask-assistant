import os
from functools import partial
import requests

from flask import json, request as flask_request

# from flask_assistant import logger
from flask_assistant.core import Assistant, _dbgdump
from flask_assistant.response import _Response
from api_ai.api_ai import ApiAi
from bot_framework.connector import BotConnector


LUIS_APP_ID = os.getenv('LUIS_APP_ID')
LUIS_ENDPOINT_KEY = os.getenv('LUIS_ENDPOINT_KEY')

LUIS_ENDPOINT = 'https://westus.api.cognitive.microsoft.com/luis/v2.0/apps/{}?subscription-key={}'.format(
    LUIS_APP_ID, LUIS_ENDPOINT_KEY)


class Bot(Assistant):

    def __init__(self, app, nlp='api_ai', route='/'):
        super().__init__(app, route)

        self.init_app(app)
        self.connector = BotConnector()
        self.api = ApiAi()
        self._nlp = nlp

    @property
    def _report(self):
        _dbgdump({
            'User Message': self.request,
            'LUIS result': self.result,
            'Matched Intent': self.intent,
            'View Func': self._intent_action_funcs[self.intent].__name__,
            'Entities': self.entities
        })

    def _bot_framework_request(self, verify=False):
        raw_body = flask_request.data
        if verify:
            self.connector.verify(flask_request)
        _dbgdump('BotFrameworkRequest:')
        _dbgdump(json.loads(raw_body), indent=3)
        return json.loads(raw_body)

    def _query_luis(self, message, *args, **kwargs):
        query = LUIS_ENDPOINT + '&q={}&timezoneOffset=0.0&verbose=true'.format(message)
        result = requests.get(query).text
        _dbgdump(json.loads(result))
        return json.loads(result)

    def _query_api(self, message, *args, **kwargs):
        result = self.api.post_query(message).text
        _dbgdump('API.AI NLP Results:')
        _dbgdump(json.loads(result))
        return json.loads(result)

    def _process_language(self):
        message = self.request['text']
        if 'api' in self._nlp:
            self._nlp_result = self._query_api(message)
            self.intent = self._nlp_result['result']['metadata']['intentName']
            self.context_in = []

        else:
            self._nlp_result = self._query_luis(message)
            self.intent = self.nlp_result['topScoringIntent']['intent']
            self.entities = self.nlp_result['entities']

        _dbgdump('Matched Intent: {}'.format(self.intent))

    def _flask_assitant_view_func(self, *args, **kwargs):
        self.request = self._bot_framework_request()
        self.connector.build_reply_from_request()

        if self.request['type'] == 'ping':
            return 'Connection Successful!', 200

        if self.request['type'] != 'message':
            _dbgdump('Not a message: {}'.format(self.request['type']))
            return 'not a message', 204

        self._process_language()

        view_func = self._match_view_func()
        result = self._map_intent_to_view_func(view_func)()

        if isinstance(result, BotConnector):
            return result.send()
        elif isinstance(result, _Response):
            return result.render_response()
        return result

    def _map_intent_to_view_func(self, view_func):
        _dbgdump('Mapping {} to {} function'.format(self.intent, view_func.__name__))
        arg_names = self._func_args(view_func)
        if 'api' in self._nlp:
            arg_values = self._map_params_to_view_args(arg_names)
        else:
            arg_values = self._luis_map_params_to_view_args(arg_names)
        return partial(view_func, *arg_values)

    @property
    def _missing_params(self):  # TODO: fill missing slot from default
        params = self._nlp_result['result']['parameters']
        missing = []
        for p_name in params:
            if params[p_name] == '':
                missing.append(p_name)

        return missing

    def _luis_map_params_to_view_args(self, arg_names):  # TODO map to correct name
        arg_values = {}
        intent_map = self._intent_mappings.get(self.intent)

        for arg_name in arg_names:
            arg_values[arg_name] = []  # may recieve multiple entities of the same type
            mapped_name = intent_map.get(arg_name, arg_name)

            for entity in self.entities:
                entity_type = entity['type']
                child = None
                value = None
                if '::' in entity['type']:
                    entity_type, child = entity['type'].split('::')
                    # entity_type, child = parent_child[0], parent_child[1]

                if mapped_name in entity_type:
                    # for built-in entities like datetime
                    if 'resolution' in entity.keys():
                        value = entity['resolution']
                        arg_values[arg_name].append(value)
                        continue
                    # right now, child entities represent a consistant form of the entitiy
                    # append child as the value instead of 'entity' property allows
                    # per day or per work flow to be passed as PerDay or PerWorkFlow
                    # This may not be necessary, if not using children
                    if child:
                        arg_values[arg_name].append(child)
                        continue
                    value = entity['entity']
                    arg_values[arg_name].append(value)

        return arg_values
