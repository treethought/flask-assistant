import inspect
from functools import wraps, partial

from flask import current_app, json, request as flask_request, _app_ctx_stack
from werkzeug.local import LocalProxy

from flask_assistant import logger
from flask_assistant.response import _Response
from flask_assistant.manager import ContextManager

request = LocalProxy(lambda: current_app.assist.request)
context_in = LocalProxy(lambda: current_app.assist.context_in)
context_manager = LocalProxy(lambda: current_app.assist.context_manager)


class Assistant(object):
    """Central Interface for interacting with Google Actions via Api.ai.

    The Assitant object routes requests to :func:`action` decorated functions.

    The assistant object maps requests recieved from an API.ai agent to Intent-specific view functions.
    The view_functions can be properly matched depending on required parameters and contexts.
    These requests originate from Google Actions and are sent to the Assitant object
    after through API.ai's infrastrcutre


    Keyword Arguments:
            app {Flask object} -- App instance - created with Flask(__name__) (default: {None})
            route {str} -- entry point to which initial Alexa Requests are forwarded (default: {None})


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

        app.assist = self
        app.add_url_rule(self._route, view_func=self._flask_assitant_view_func, methods=['POST'])

    @property
    def request(self):
        """Local Proxy refering to the request JSON recieved from API.AI"""
        return getattr(_app_ctx_stack.top, '_assist_request', None)

    @request.setter
    def request(self, value):
        _app_ctx_stack.top._assist_request = value

    @property
    def intent(self):
        """Local Proxy refering to the name of the intent contained in the API.AI request"""
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
    def context_manager(self):
        """LocalProxy refering to the app's instance of the  :class: `ContextManager`.

        Interface for adding and accessing contexts and their parameters
        """
        return getattr(_app_ctx_stack.top, '_assist_context_manager', ContextManager())

    @context_manager.setter
    def context_manager(self, value):
        _app_ctx_stack.top._assist_context_manager = value

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
        """
        def decorator(f):
            action_funcs = self._intent_action_funcs.get(intent, [])
            action_funcs.append(f)
            self._intent_action_funcs[intent] = action_funcs

            self._intent_mappings[intent] = mapping
            self._intent_converts[intent] = convert
            self._intent_defaults[intent] = default

            @wraps(f)
            def wrapper(*args, **kw):
                self._flask_assitant_view_func(*args, **kw)
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
                self._flask_assitant_view_func(*args, **kw)
            return f
        return decorator

    def fallback(self):
        def decorator(f):
            self._fallback_response = f
            return f

    def _api_request(self, verify=True):
        raw_body = flask_request.data
        _api_request_payload = json.loads(raw_body)

        return _api_request_payload

    def _dump_view_info(self, view_func=lambda: None):
        _infodump('Result: Matched {} intent to {} func'.format(self.intent, view_func.__name__))

    def _flask_assitant_view_func(self, *args, **kwargs):
        self.request = self._api_request(verify=False)
        _dbgdump(self.request['result'])

        self.intent = self.request['result']['metadata']['intentName']
        self.context_in = self.request['result'].get('contexts', [])
        self._update_contexts()

        view_func = self._match_view_func()
        _dbgdump('Matched view func - {}'.format(self.intent, view_func))
        result = self._map_intent_to_view_func(view_func)()

        if result is not None:
            if isinstance(result, _Response):
                return result.render_response()
            return result
        return "", 400

    def _update_contexts(self):
        temp = self.context_manager
        temp.update(self.context_in)
        self.context_manager = temp


    def _match_view_func(self):
        view_func = None

        if self.context_in:
            view_func = self._choose_context_view()

        elif self._missing_params:
            prompts = self._intent_prompts.get(self.intent)
            if prompts:
                param_choice = self._missing_params.pop()
                view_func = prompts.get(param_choice)

        elif len(self._intent_action_funcs[self.intent]) == 1:
            view_func = self._intent_action_funcs[self.intent][0]

        if not view_func:
            view_func = self._intent_action_funcs[self.intent][0]
            _errordump('No view func matched')
            _errordump({
                'intent recieved': self.intent,
                'recieved parameters': self.request['result']['parameters'],
                'required args': self._func_args(view_func),
                'conext_in': self.context_in,
                'matched view_func': view_func.__name__
            })

        return view_func

    @property
    def _context_views(self):
        """Returns view functions for which the context requirements are met"""
        possible_views = []
        recieved_contexts = [c['name'] for c in self.context_in]
        # recieved_contexts = [c['name'] for c in self.context_manager.active]


        for func in self._func_contexts:
            requires = list(self._func_contexts[func])
            met = []
            for req_context in requires:
                if req_context in recieved_contexts:
                    met.append(req_context)

            if set(met) == set(requires) and len(requires) <= len(recieved_contexts):
                # if not requires:
                # import ipdb; ipdb.set_trace()
                possible_views.append(func)

        return possible_views

    def _choose_context_view(self):
        choice = None
        for view in self._context_views:
            if view in self._intent_action_funcs[self.intent]:
                choice = view
        if choice:
            return choice
        else:
            _errordump('')
            _errordump('No view matched for {} with context'.format(self.intent))
            _errordump('intent: {}'.format(self.intent))
            _errordump('possible biews: {}'.format(self._context_views))
            _errordump('intent action funcs: {}'.format(self._intent_action_funcs[self.intent]))

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

    def _map_params_to_view_args(self, arg_names): # TODO map to correct name
        arg_values = []
        mapping = self._intent_mappings.get(self.intent)
        params = self.request['result']['parameters']

        for arg_name in arg_names:
            entity_mapping = mapping.get(arg_name, arg_name)
            # param name cant have '.',
            # so when registered, the sys. is stripped,
            # and must be stripped when looking up in request
            mapped_param_name = entity_mapping.replace('sys.', '') 
            value = params.get(mapped_param_name)  # params declared in GUI present in request
            
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
