from flask import current_app, json, request as flask_request, _app_ctx_stack
from werkzeug.local import LocalProxy

import collections
from functools import wraps, partial
import inspect

from . import logger
from .response import _Response
from pprint import pprint
from copy import copy


request = LocalProxy(lambda: current_app.assist.request)
context_in = LocalProxy(lambda: current_app.assistant.contexts)

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
        self._required_contexts = {}
        self._context_funcs = {}
        self._func_contexts = {}

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
    def intent(self):
        return getattr(_app_ctx_stack.top, '_assist_intent', None)

    @intent.setter
    def intent(self, value):
        _app_ctx_stack.top._assist_intent = value

    @property
    def context_in(self):
        """Local Proxy refering to context objects contained within current session"""
        return getattr(_app_ctx_stack.top, '_assist_context_in', [])

    @context_in.setter
    def context_in(self, value):
        _app_ctx_stack.top._assist_context_in = value

    @property
    def session_id(self):
        return getattr(_app_ctx_stack.top, '_assist_session_id', None)

    def _register_context_to_func(self, intent_name, context=[]):
        required = self._required_contexts.get(intent_name)
        if required:
            required.extend(context)
        else:
            self._required_contexts[intent_name] = []
            self._required_contexts[intent_name].extend(context)

    def context(self, *context_names):

        def decorator(f):
            func_requires = self._func_contexts.get(f)

            if not func_requires:
                self._func_contexts[f] = []

            self._func_contexts[f].extend(context_names)

            def wrapper(*args, **kw):
                return f(*args, with_context=context_names, **kw)
            return wrapper
        return decorator


    def action(self, intent, mapping={}, convert={}, default={}, with_context=[], *args, **kw):
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
            self._intent_action_funcs[intent] = f
            self._intent_mappings[intent] = mapping
            self._intent_converts[intent] = convert
            self._intent_defaults[intent] = default

            @wraps(f)
            def wrapper(*args, **kw):
                self._flask_view_func(*args, **kw)
            return f
        return decorator

    def prompt_for(self, next_param, intent):
        """Decorates a function to prompt for an action's required parameter.

        The wrapped function is called if next_param was not recieved with the given intent's
        request and is required for the fulfillment of the intent's action.

        Arguments:
            next_param {str} -- name of the parameter required for action function
            intent_name {str} -- name of the intent the dependent action belongs to
        """
        def decorator(f):
            prompts = self._intent_prompts.get(intent)
            if prompts:
                prompts[next_param] = f
            else:
                self._intent_prompts[intent] = {}
                self._intent_prompts[intent][next_param] = f

            @wraps(f)
            def wrapper(*args, **kw):
                self._flask_view_func(*args, **kw)
            return f
        return decorator

    def _api_request(self, verify=True):
        raw_body = flask_request.data
        _api_request_payload = json.loads(raw_body)

        return _api_request_payload

    def _dump_view_info(self, view_func=lambda: None):
        _infodump('Result: Matched {} intent to {} func'.format(self.intent, view_func.__name__))
        _dbgdump({
            'intent recieved': self.intent,
            'recieved parameters': self.request['result']['parameters'],
            'required args': self._func_args(view_func),
            'conext_in': self.context_in,
            'matched view_func': view_func.__name__
        })

    def _flask_view_func(self, *args, **kwargs):
        self.request = self._api_request(verify=False)
        _infodump(self.request['result'])

        self.intent = self.request['result']['metadata']['intentName']
        self.context_in = self.request['result'].get('contexts', [])
        view_func = self._match_view_func()

        result = self._map_intent_to_view_func(view_func)()

        if result is not None:
            if isinstance(result, _Response):
                return result.render_response()
            return result
        return "", 400

    # def _context_requirements_met(self):
    #     remaining = copy(self._required_contexts[self.intent])

    #     for con in self.context_in:
    #         _dbgdump('checking if {} context is met'.format(con['name']))
    #         if con['name'] in remaining:
    #             _dbgdump('{} requiremnt met'.format(con['name']))
    #             remaining.remove(con['name'])
    #         else:
    #             _dbgdump('{} requiremnt was not met'.format(con['name']))

        # if len(remaining) < 1:
        #     _dbgdump('requirements met')
        #     return True

    def _match_view_func(self):
        action_func = self._intent_action_funcs[self.intent]
        view_func = None

        if not self.context_in and not self._missing_params:
            _dbgdump('Matched {} intent to {} func without context'.format(self.intent, action_func))
            return action_func

        elif self.context_in and action_func in self._context_views:
            view_func = action_func
            _dbgdump('Matched {} intent to {} func via context'.format(self.intent, view_func.__name__))

        elif self._missing_params:
            param_choice = self._missing_params.pop()
            view_func = self._intent_prompts[self.intent].get(param_choice)
            _dbgdump('Matched {} intent to {} func as {} prompt'.format(self.intent, view_func.__name, param_choice))

        else:
            return action_func

        if not view_func:
            _errordump('No view func matched for {}'.format(self.intent))
        return view_func

    @property
    def _context_views(self):
        possible_views = []
        recieved_contexts = [c['name'] for c in self.context_in]

        for func in self._func_contexts:
            requires = copy(self._func_contexts[func])

            for req_context in requires:
                if req_context in recieved_contexts:
                    requires.remove(req_context)

            if not requires:
                possible_views.append(func)

        view_names = [f.__name__ for f in possible_views]  # for logging
        _dbgdump('Matched {} as possible views for {}'.format(view_names, recieved_contexts))
        return possible_views

    @property
    def _missing_params(self):  # TODO: fill missing slot from default
        params = self.request['result']['parameters']
        missing = []
        for p_name in params:
            if params[p_name] == '':
                missing.append(p_name)

        return missing

    def _func_args(self, f):
        argspec = inspect.getargspec(f)
        return argspec.args

    def _map_intent_to_view_func(self, view_func):
        arg_names = self._func_args(view_func)
        arg_values = self._map_params_to_view_args(arg_names)
        return partial(view_func, *arg_values)

    def _map_params_to_view_args(self, arg_names):
        arg_values = []
        mapping = self._intent_mappings.get(self.intent)
        params = self.request['result']['parameters']

        for arg_name in arg_names:
            mapped_name = mapping.get(arg_name, arg_name)
            value = params.get(mapped_name)  # params declared in GUI present in request

            if not value:  # params not declared, so must look in contexts
                value = self._map_arg_from_context(arg_name)
            arg_values.append(value)

        return arg_values

    def _map_arg_from_context(self, arg_name):
        for context_obj in self.context_in:
            if arg_name in context_obj['parameters']:
                return context_obj['parameters'][arg_name]


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
