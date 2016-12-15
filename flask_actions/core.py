from flask import current_app, json, request as flask_request, _app_ctx_stack
from werkzeug.local import LocalProxy

from functools import wraps, partial
import inspect
from pprint import pprint

from . import logger
from .response import _Response


request = LocalProxy(lambda: current_app._app_ctx_stack.request)
result = LocalProxy(lambda: current_app._app_ctx_stack.result)
contexts = LocalProxy(lambda: current_app._app_ctx_stack.contexts)
metadata = LocalProxy(lambda: current_app._app_ctx_stack.metadata)
intent = LocalProxy(lambda: current_app._app_ctx_stack.intent)

_converters = []





import collections


class Agent(object):
    """Central Interface for itneracting with the Google Actions via Api.ai"""

    def __init__(self, app=None, route='/'):

        self.app = app
        self._route = route
        self._intent_action_funcs = {}
        self._intent_mappings = {}
        self._intent_converts = {}
        self._intent_defaults = {}
        self._intent_prompts = {}

        if app is not None:
            self.init_app(app)

    def init_app(self, app):

        if self._route is None:
            raise TypeError("route is a required argument when app is not None")

        app.agent = self

        app.add_url_rule(self._route, view_func=self._flask_view_func, methods=['POST'])

    @property
    def request(self):
        return getattr(_app_ctx_stack.top, '_agent_request', None)

    @request.setter
    def request(self, value):
        _app_ctx_stack.top._agent_request = value

    @property
    def context(self):
        return getattr(_app_ctx_stack.top, '_agent_context', None)

    @context.setter
    def context(self, value):
        _app_ctx_stack.top._agent_context = value

    @property
    def action(self):
        return getattr(_app_ctx_stack.top, '_agent_action', None)

    @action.setter
    def action(self, value):
        _app_ctx_stack.top._agent_action = value

    @property
    def params(self):
        return getattr(_app_ctx_stack.top, '_agent_params', None)

    @params.setter
    def params(self, value):
        _app_ctx_stack.top._agent_params = value

    @property
    def metadata(self):
        return getattr(_app_ctx_stack.top, '_agent_metadata', None)

    @metadata.setter
    def metadata(self, value):
        _app_ctx_stack.top._agent_metadata = value

    @property
    def _slot_filling(self):
        return sef.metadata.get('webhookForSlotFillingUsed', None)

    @property
    def session_id(self):
        return getattr(_app_ctx_stack.top._agent_request, 'session_id', None)

    @property
    def timestamp(self):
        return getattr(_app_ctx_stack.top._agent_request, 'session_id', None)

    def intent(self, intent_name, mapping={}, convert={}, default={}, in_context=False):

        def decorator(f):
            self._intent_action_funcs[intent_name] = f
            self._intent_mappings[intent_name] = mapping
            self._intent_converts[intent_name] = convert
            self._intent_defaults[intent_name] = default

            @wraps(f)
            def wrapper(*args, **kw):
                self._flask_view_func(*args, **kw)
            return f
        return decorator

    def fill_slot(self, intent_name, next_param):

        def decorator(f):
            prompts = self._intent_prompts.get(intent_name)
            if prompts:
                prompts[next_param] = f
            else:
                self._intent_prompts[intent_name] = {}
                self._intent_prompts[intent_name][next_param] = f

            @wraps(f)
            def wrapper(*args, **kw):
                self._flask_view_func(*args, **kw)
            return f
        return decorator


    def _api_request(self, verify=True):
        raw_body = flask_request.data
        _api_request_payload = json.loads(raw_body)

        return _api_request_payload

    def _flask_view_func(self, *args, **kwargs):
        payload = self._api_request(verify=False)
        # _dbgdump(payload)
        pprint(payload)

        self.request = payload

        self.query = payload['result']['resolvedQuery']
        self.action = payload['result']['action']
        self.contexts = payload['result']['contexts']
        self.metadata = payload['result']['metadata']
        # self.slot_filling = self.request['result']['metadata']['webhookForSlotFillingUsed']

        result = None
        intent_name = payload['result']['metadata']['intentName']

        result = self._map_intent_to_view_func(intent_name)()

        if result is not None:
            if isinstance(result, _Response):
                return result.render_response()
            return result
        return "", 400


    def _map_intent_to_view_func(self, intent_name):

        action_func = self._intent_action_funcs[intent_name]
        missing_params = self._missing_params(intent_name)

        # TODO: fill missing slot from default
        if not missing_params:
            # print('No missing params, trigger action\n')
            action_func = self._intent_action_funcs[intent_name]
            arg_names = inspect.getargspec(action_func).args
            mapped_args = self._map_args(intent_name, arg_names)
            arg_values = self._map_params_to_view_args(intent_name, arg_names)
            return partial(action_func, *arg_values)

        else:  # TODO priority ordering of prompts
            # print('Missing parameters!\n')
            for param in missing_params:
                # print('missing {}'.format(param))
                prompt_func = self._intent_prompts[intent_name].get(param)
                # print('prompt function is {}!\n'.format(prompt_func))
                if prompt_func:
                    arg_names = inspect.getargspec(prompt_func).args
                    mapped_args = self._map_args(intent_name, arg_names)
                    arg_values = self._map_params_to_view_args(intent_name, arg_names)
                    return partial(prompt_func, *arg_values)

    def _map_args(self, intent_name, arg_names):
        mapping = self._intent_mappings.get(intent_name)
        mapped_names = []
        for arg_name in arg_names:
            mapped_names.append(mapping.get(arg_name, arg_name))

        return mapped_names

    def _missing_params(self, intent_name, use_default=True):
        params = self.request['result']['parameters']
        missing = []
        for p_name in params:
            if params[p_name] == '':
                missing.append(p_name)
        return missing

    def _map_params_to_view_args(self, view_name, arg_names):

        arg_values = []
        convert = self._intent_converts.get(view_name)
        default = self._intent_defaults.get(view_name)
        mapping = self._intent_mappings.get(view_name)

        convert_errors = {}

        params = self.request['result']['parameters']

        for arg_name in arg_names:
            mapped_name = mapping.get(arg_name, arg_name)
            arg_value = params.get(mapped_name)

            if arg_value is None or arg_value == "":
                if arg_name in default:
                    default_value = default[arg_name]
                    if isinstance(default_value, collections.Callable):
                        default_value = default_value()
                    arg_value = default_value
            elif arg_name in convert:
                shorthand_or_function = convert[arg_name]
                if shorthand_or_function in _converters:
                    shorthand = shorthand_or_function
                    convert_func = _converters[shorthand]
                else:
                    convert_func = shorthand_or_function
                try:
                    arg_value = convert_func(arg_value)
                except Exception as e:
                    convert_errors[arg_name] = e
            arg_values.append(arg_value)
        self.convert_errors = convert_errors
        return arg_values


def _dbgdump(obj, indent=2, default=None, cls=None):
    msg = json.dumps(obj, indent=indent, default=default, cls=cls)
    logger.debug(msg)
