from flask import current_app, json, request as flask_request, _app_ctx_stack
from werkzeug.local import LocalProxy

import collections
from functools import wraps, partial
import inspect

from . import logger
from .response import _Response


request = LocalProxy(lambda: current_app.assist.request)
# result = LocalProxy(lambda: current_app.assistant.result)
contexts = LocalProxy(lambda: current_app.assistant.contexts)
# metadata = LocalProxy(lambda: current_app.assistant.metadata)
# intent = LocalProxy(lambda: current_app.assistant.intent)

_converters = []


class Assistant(object):
    """Central Interface for interacting with Google Actions via Api.ai.

    The Assitant object routes requests 

    The construtor is passed a Flask App instance and a url enpoint.
    Route provides the entry point for the skill, and must be provided if an app is given.

    Keyword Arguments:
            app {Flask object} -- App instance - created with Flask(__name__) (default: {None})
            route {str} -- entry point to which initial Alexa Requests are forwarded (default: {None})


    The assistant object maps requests recieved from an API.ai agent to Intent-specific view functions.
    The view_functions can be properly matched depending on required parameters and contexts.
    These requests originate from Google Actions and are sent to the Assitant object
    after through API.ai's infrastrcutre

    """

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
        """Local Proxy refering to the request JSON recieved from API/Actions"""
        return getattr(_app_ctx_stack.top, '_assist_request', None)

    @request.setter
    def request(self, value):
        _app_ctx_stack.top._assist_request = value

    @property
    def contexts(self):
        """Local Proxy refering to context objects contained within current session"""
        return getattr(_app_ctx_stack.top, '_assist_contexts', None)

    @contexts.setter
    def contexts(self, value):
        _app_ctx_stack.top._assist_contexts = value

    @property
    def session_id(self):
        return getattr(_app_ctx_stack.top, '_assist_session_id', None)

    def action(self, intent_name, mapping={}, convert={}, default={}, with_context=None):
        """Decorates an intent's Action view function.
        
        The wrapped function is called when a request with the
        given intent_name is recieved along with all required parameters.
        
        Arguments:
            intent_name {str} -- name of the intent the action belongs to
        
        Keyword Arguments:
            mapping {dict} -- Maps function arguments to request parameters of a different name
                                default: {}
            convert {dict} -- Converts request parameter values to data types before assignment to function arguments.
                                default: {}
            default {dict} --  Provides default values for function arguments if Actions/API.ai request
                                returns no corresponding parameter, or a slot with an empty value.
                                Providing a default will over-ride any prompt functions for provided arguments
                                default: {}
            in_context {str} -- [Restricts execution of wrapped function to certain contexts] (default: {False})
        
        """
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

    def prompt_for(self, next_param, intent_name):
        """Decorates a function to prompt for an action's required parameter.
        
        The wrapped function is called if next_param was not recieved with the given intent's
        request and is required for the fulfillment of the intent's action.
        
        Arguments:
            next_param {str} -- name of the parameter required for action function
            intent_name {str} -- name of the intent the dependent action belongs to
        """

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
        self.request = self._api_request(verify=False)
        _dbgdump(self.request)

        result = None
        intent_name = self.request['result']['metadata']['intentName']
        view_func = self._match_view_func(intent_name)

        result = self._map_intent_to_view_func(intent_name, view_func)()

        if result is not None:
            if isinstance(result, _Response):
                return result.render_response()
            return result
        return "", 400

    def _missing_params(self, intent_name, use_default=True):  # TODO: fill missing slot from default
        params = self.request['result']['parameters']
        missing = []
        for p_name in params:
            if params[p_name] == '':
                missing.append(p_name)

        return missing

    def _match_view_func(self, intent_name): # TODO: context conditional
        missing_params = None

        if self.request['result']['actionIncomplete']:
            missing_params = self._missing_params(intent_name)

        if not missing_params:
            return self._intent_action_funcs[intent_name]

        else:
            param_choice = missing_params.pop()
            return self._intent_prompts[intent_name].get(param_choice)

    def _map_intent_to_view_func(self, intent_name, view_func):
        argspec = inspect.getargspec(view_func)
        arg_names = argspec.args
        arg_values = self._map_params_to_view_args(intent_name, arg_names)
        return partial(view_func, *arg_values)


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
