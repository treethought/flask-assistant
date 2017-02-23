from flask import current_app, json, request as flask_request, _app_ctx_stack, make_response, abort

from werkzeug.local import LocalProxy
import requests
import os
from functools import wraps, partial
from flask_assistant import logger
from flask_assistant.core import Assistant
from luis.connector import BotConnector


from pprint import pprint


LUIS_APP_ID = os.getenv('LUIS_APP_ID')
LUIS_ENDPOINT_KEY = os.getenv('LUIS_ENDPOINT_KEY')

LUIS_ENDPOINT = 'https://westus.api.cognitive.microsoft.com/luis/v2.0/apps/{}?subscription-key={}'.format(
    LUIS_APP_ID, LUIS_ENDPOINT_KEY)

# connector = LocalProxy(lambda: current_app.assist.connector)

_converters = {''}


class Bot(Assistant):
    """The Bot object serves as the interface for manning requests from the

        Central Interface for for handling communication between Microsoft Bot Framework and Luis applications.

        The Bot object receives requests from the Bot Framework pertaining to a user's request.
        The incoming request is used to query our LUIS application, and match the LUIS intent to the proper view function.

     """

    def __init__(self, app, route='/'):
        super().__init__(app, route)

        self.init_app(app)
        self.connector = BotConnector()

    def init_app(self, app):

        if self._route is None:
            raise TypeError("route is a required argument when app is not None")

        app.assist = self
        app.add_url_rule(self._route, view_func=self._flask_assitant_view_func, methods=['POST'])

    def action(self, intent, mapping={}, convert={}, default={}, with_context=[], *args, **kw):
        """Decorates an intent's Action view function.

            The wrapped function is called when a request with the
            given intent_name is recieved along with all required parameters.
        """
        def decorator(f):
            # action_funcs = self._intent_action_funcs.get(intent, [])
            # action_funcs.append(f)
            # self._intent_action_funcs[intent] = action_funcs
            self._intent_action_funcs[intent] = f
            self._intent_mappings[intent] = mapping
            self._intent_converts[intent] = convert
            self._intent_defaults[intent] = default

            @wraps(f)
            def wrapper(*args, **kw):
                self._flask_assitant_view_func(*args, **kw)
            return f
        return decorator

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
        _dbgdump(json.loads(raw_body), indent=3)
        return json.loads(raw_body)

    def _query_luis(self, message, *args, **kwargs):
        query = LUIS_ENDPOINT + '&q={}&timezoneOffset=0.0&verbose=true'.format(message)
        result = requests.get(query).text
        _dbgdump(json.loads(result))
        return json.loads(result)

    def _flask_assitant_view_func(self, *args, **kwargs):
        # import ipdb; ipdb.set_trace()
        self.request = self._bot_framework_request(verify=False)

        if self.request['type'] == 'ping':
            return 'Connection Successful!!!', 200

        if self.request['type'] != 'message':
            print(self.request['type'])
            return 'not a message', 204

        self.result = self._query_luis(self.request['text'])

        self.connector.build_reply_from_request()

        self.intent = self.result['topScoringIntent']['intent']
        self.entities = self.result['entities']

        view_func = self._intent_action_funcs[self.intent]
        # self._report()

        result = self._map_intent_to_view_func(view_func)()
        if isinstance(result, BotConnector):
            return result.send()
        return result

    def _map_intent_to_view_func(self, view_func):
        arg_names = self._func_args(view_func)
        arg_values = self._map_params_to_view_args(arg_names)
        # _dbgdump(arg_values)
        return partial(view_func, **arg_values)

    def _map_params_to_view_args(self, arg_names):  # TODO map to correct name
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

        # _dbgdump(arg_values)
        return arg_values

    # def map_datetime(self, entity_object):


def _dbgdump(obj, indent=2, default=None, cls=None):
    msg = json.dumps(obj, indent=indent, default=default, cls=cls)
    logger.debug(msg)


def _infodump(obj, indent=2, default=None, cls=None):
    msg = json.dumps(obj, indent=indent, default=default, cls=cls)
    logger.info(msg)


def _warndump(obj, indent=2, default=None, cls=None):
    msg = json.dumps(obj, indent=indent, default=default, cls=cls)
    logger.warn(msg)


def _errordump(obj, indent=2, default=None, cls=None):
    msg = json.dumps(obj, indent=indent, default=default, cls=cls)
    logger.error(msg)
