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
            

            if func_requires:
                func_requires.extend(*context_names)
            else:
                self._func_contexts[f] = [*context_names]

            def wrapper(*args, **kw):
                f(with_context=context_names, *args, **kwargs)

            return wrapper
            _dbgdump('in context decorator')
            _dbgdump('{} requires {} context'.format(f, context_name))
        return decorator

    # def context(self, name):

    #     def decorator(f):
    #         context_funcs = self._context_funcs.get(name, None)
    #         if context_funcs:
    #             context_funcs.append(f)
    #         else:
    #             self._context_funcs[name] = [f]

    #         @wraps(f)
    #         def wrapper(*args, **kw):
    #             print('in wrapper for context {}'.format(name))
    #         return f
    #     return decorator

    def action(self, intent, mapping={}, convert={}, default={}, with_context=[], **kw):
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

            self._register_context_to_func(intent, with_context)
            _dbgdump('In action decorator')
            _dbgdump('{} requires {} contexts'.format(f, with_context))
            _dbgdump('registered {} to {}'.format(self._required_contexts[intent], intent))

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

    def _flask_view_func(self, *args, **kwargs):
        self.request = self._api_request(verify=False)
        _dbgdump(self.request)

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

    def _match_view_func(self):  # TODO: context conditional
        intent_name = self.intent

        if self.context_in:
            possible_views = self._match_context()
            for view_func in possible_views:
                if view_func is self._intent_action_funcs[intent_name]:
                    return view_func
                # if self._context_requirements_met and not self._missing_params:
                #     pass
        if not self._missing_params:
            return self._intent_action_funcs[intent_name]

        else:
            param_choice = self._missing_params.pop()
            return self._intent_prompts[intent_name].get(param_choice)


    def _match_context(self):
        possible_views = []
        recieved_contexts = [c['name'] for c in self.context_in]

        for func in self._func_contexts:
            requires = copy(self._func_contexts[func])
            for req_context in requires:
                if req_context in recieved_contexts:
                    requires.remove(req_context)
                    _dbgdump('{} requirement was met for {}'.format(req_context, func))

                else:
                    _dbgdump('{} missing {}'.format(func, req_context))

            if not requires:
                _dbgdump('requirements met for {}'.format(func))
                possible_views.append(func)

        _dbgdump('Matched {} as possible views for {}'.format(possible_views, recieved_contexts))
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
        # argspec = inspect.getargspec(view_func)
        # arg_names = argspec.args
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


    # def _map_params_to_view_args(self, view_name, arg_names):

    #     arg_values = []
    #     convert = self._intent_converts.get(view_name)
    #     default = self._intent_defaults.get(view_name)
    #     mapping = self._intent_mappings.get(view_name)

    #     convert_errors = {}

    #     params = self.request['result']['parameters']

    #     for arg_name in arg_names:
    #         mapped_name = mapping.get(arg_name, arg_name)
    #         arg_value = params.get(mapped_name)

    #         if arg_value is None or arg_value == "":
    #             if arg_name in default:
    #                 default_value = default[arg_name]
    #                 if isinstance(default_value, collections.Callable):
    #                     default_value = default_value()
    #                 arg_value = default_value
    #         elif arg_name in convert:
    #             shorthand_or_function = convert[arg_name]
    #             if shorthand_or_function in _converters:
    #                 shorthand = shorthand_or_function
    #                 convert_func = _converters[shorthand]
    #             else:
    #                 convert_func = shorthand_or_function
    #             try:
    #                 arg_value = convert_func(arg_value)
    #             except Exception as e:
    #                 convert_errors[arg_name] = e
    #         arg_values.append(arg_value)
    #     self.convert_errors = convert_errors
    #     return arg_values


def _dbgdump(obj, indent=2, default=None, cls=None):
    msg = json.dumps(obj, indent=indent, default=default, cls=cls)
    logger.debug(msg)

def _infodump(obj, indent=2, default=None, cls=None):
    msg = json.dumps(obj, indent=indent, default=default, cls=cls)
    logger.info(msg)
