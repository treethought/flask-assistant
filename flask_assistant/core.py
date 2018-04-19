import inspect
import sys
import os
from functools import wraps, partial


from flask import current_app, json, request as flask_request, _app_ctx_stack
from werkzeug.local import LocalProxy

from flask_assistant import logger
from flask_assistant.response import _Response
from flask_assistant.manager import ContextManager
from api_ai.api import ApiAi
from io import StringIO


def find_assistant():  # Taken from Flask-ask courtesy of @voutilad
    """
    Find our instance of Assistant, navigating Local's and possible blueprints.

    Note: This only supports returning a reference to the first instance
    of Assistant found.
    """
    if hasattr(current_app, 'assist'):
        return getattr(current_app, 'assist')
    else:
        if hasattr(current_app, 'blueprints'):
            blueprints = getattr(current_app, 'blueprints')
            for blueprint_name in blueprints:
                if hasattr(blueprints[blueprint_name], 'assist'):
                    return getattr(blueprints[blueprint_name], 'assist')


request = LocalProxy(lambda: find_assistant().request)
intent = LocalProxy(lambda: find_assistant().intent)
context_in = LocalProxy(lambda: find_assistant().context_in)
context_manager = LocalProxy(lambda: find_assistant().context_manager)


class Assistant(object):
    """Central Interface for interacting with Google Actions via Api.ai.

    The Assistant object routes requests to :func:`action` decorated functions.

    The assistant object maps requests received from an API.ai agent to Intent-specific view functions.
    The view_functions can be properly matched depending on required parameters and contexts.
    These requests originate from Google Actions and are sent to the Assistant object
    after through API.ai's infrastructure.


    Keyword Arguments:
            app {Flask object} -- App instance - created with Flask(__name__) (default: {None})
            blueprint {Flask Blueprint} -- Flask Blueprint instance to initialize (Default: {None})
            route {str} -- entry point to which initial Alexa Requests are forwarded (default: {None})
            dev_token {str} - Dialogflow dev access token used to register and retrieve agent resources
            client_token {str} - Dialogflow client access token required for querying agent
    """

    def __init__(self, app=None, blueprint=None, route=None, dev_token=None, client_token=None):

        self.app = app
        self.blueprint = blueprint
        self._route = route
        self._intent_action_funcs = {}
        self._intent_mappings = {}
        self._intent_converts = {}
        self._intent_defaults = {}
        self._intent_fallbacks = {}
        self._intent_prompts = {}
        self._intent_events = {}
        self._required_contexts = {}
        self._context_funcs = {}
        self._func_contexts = {}

        self.api = ApiAi(dev_token, client_token)

        if route is None and app is not None:

            logger.warn("""WARNING:
                No route was provided for the Assistant object, but a flask `app` object given
                The Assistant will be mapped to the app's '/' endpoint.
                If this is a problem please initialize the Assitant with the 'route' parameter
                """)

            self._route = '/'

        if app is not None:
            self.init_app(app)
        elif blueprint is not None:
            self.init_blueprint(blueprint)

    def init_app(self, app):

        if self._route is None:
            raise TypeError("route is a required argument when app is not None")

        app.assist = self
        app.add_url_rule(self._route, view_func=self._flask_assitant_view_func, methods=['POST'])

    # Taken from Flask-ask courtesy of @voutilad
    def init_blueprint(self, blueprint, path='templates.yaml'):
        """Initialize a Flask Blueprint, similar to init_app, but without the access
        to the application config.

        Keyword Arguments:
            blueprint {Flask Blueprint} -- Flask Blueprint instance to initialize (Default: {None})
            path {str} -- path to templates yaml file, relative to Blueprint (Default: {'templates.yaml'})
        """
        if self._route is not None:
            raise TypeError("route cannot be set when using blueprints!")

        # we need to tuck our reference to this Ask instance into the blueprint object and find it later!
        blueprint.assist = self

        # BlueprintSetupState.add_url_rule gets called underneath the covers and
        # concats the rule string, so we should set to an empty string to allow
        # Blueprint('blueprint_api', __name__, url_prefix="/assist") to result in
        # exposing the rule at "/assist" and not "/assist/".
        blueprint.add_url_rule("", view_func=self._flask_assitant_view_func, methods=['POST'])
        # blueprint.jinja_loader = ChoiceLoader([YamlLoader(blueprint, path)])

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
            required.extend(list(set(context) - set(required)))
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

    def action(self, intent_name, is_fallback=False, mapping={}, convert={}, default={}, with_context=[], events=[], *args, **kw):
        """Decorates an intent_name's Action view function.

            The wrapped function is called when a request with the
            given intent_name is recieved along with all required parameters.
        """
        def decorator(f):
            action_funcs = self._intent_action_funcs.get(intent_name, [])
            action_funcs.append(f)
            self._intent_action_funcs[intent_name] = action_funcs

            self._intent_mappings[intent_name] = mapping
            self._intent_converts[intent_name] = convert
            self._intent_defaults[intent_name] = default
            self._intent_fallbacks[intent_name] = is_fallback
            self._intent_events[intent_name] = events
            self._register_context_to_func(intent_name, with_context)

            @wraps(f)
            def wrapper(*args, **kw):
                self._flask_assitant_view_func(*args, **kw)
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

    def _flask_assitant_view_func(self, nlp_result=None, *args, **kwargs):
        if nlp_result:  # pass API query result directly
            self.request = nlp_result
        else:  # called as webhook
            self.request = self._api_request(verify=False)

        _dbgdump(self.request)

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

        if self.hasLiveContext():
            view_func = self._choose_context_view()

        if not view_func and self._missing_params:
            prompts = self._intent_prompts.get(self.intent)
            if prompts:
                param_choice = self._missing_params.pop()
                view_func = prompts.get(param_choice)

        if not view_func and len(self._intent_action_funcs[self.intent]) == 1:
            view_func = self._intent_action_funcs[self.intent][0]

            # TODO: Do not match func if context not satisfied

        if not view_func:
            view_func = self._intent_action_funcs[self.intent][0]
            _errordump('No view func matched')
            _errordump({
                'intent recieved': self.intent,
                'recieved parameters': self.request['result']['parameters'],
                'required args': self._func_args(view_func),
                'context_in': self.context_in,
                'matched view_func': view_func.__name__
            })

        return view_func

    def hasLiveContext(self):
        for context in self.context_in:
            if context['lifespan'] > 0:
                return True

    def run_aws_lambda(self, event):
        """Invoke the Flask Assistant application from an AWS Lambda function handler.
        Use this method to service AWS Lambda requests from a custom Assistant
        Action. This method will invoke your Flask application providing a
        WSGI-compatible environment that wraps the original Dialogflow event
        provided to the AWS API Gateway handler. Returns the output generated by
        a Flask Assistant application, which should be used as the return value
        to the AWS Lambda handler function ready for API Gateway.
        From Flask Ask and adjusted for Flask Assistant
        Example usage:
            from flask import Flask
            from flask_assistant import Assistant, ask

            app = Flask(__name__)
            assist = Assistant(app, route='/')
            logging.getLogger('flask_assistant').setLevel(logging.DEBUG)


            def lambda_handler(event, _context):
                return assist.run_aws_lambda(event)


            @assist.action('greetings')
            def greet_and_start():
                speech = "Hey! Are you male or female?"
                return ask(speech)
        """

        # Convert an environment variable to a WSGI "bytes-as-unicode" string
        enc, esc = sys.getfilesystemencoding(), 'surrogateescape'
        def unicode_to_wsgi(u):
            return u.encode(enc, esc).decode('iso-8859-1')

        # Create a WSGI-compatible environ that can be passed to the
        # application. It is loaded with the OS environment variables,
        # mandatory CGI-like variables, as well as the mandatory WSGI
        # variables.
        environ = {k: unicode_to_wsgi(v) for k, v in os.environ.items()}
        environ['REQUEST_METHOD'] = 'POST'
        environ['PATH_INFO'] = '/'
        environ['SERVER_NAME'] = 'AWS-Lambda'
        environ['SERVER_PORT'] = '80'
        environ['SERVER_PROTOCOL'] = 'HTTP/1.0'
        environ['wsgi.version'] = (1, 0)
        environ['wsgi.url_scheme'] = 'http'
        environ['wsgi.errors'] = sys.stderr
        environ['wsgi.multithread'] = False
        environ['wsgi.multiprocess'] = False
        environ['wsgi.run_once'] = True

        # Convert the event provided by the AWS Lambda handler to a JSON
        # string that can be read as the body of a HTTP POST request.
        body = event['body']
        environ['CONTENT_TYPE'] = 'application/json'
        environ['CONTENT_LENGTH'] = len(body)
        environ['wsgi.input'] = StringIO(body)

        # Start response is a required callback that must be passed when
        # the application is invoked. It is used to set HTTP status and
        # headers. Read the WSGI spec for details (PEP3333).
        headers = []
        def start_response(status, response_headers, _exc_info=None):
            headers[:] = [status, response_headers]

        # Invoke the actual Flask application providing our environment,
        # with our Assistant event as the body of the HTTP request, as well
        # as the callback function above. The result will be an iterator
        # that provides a serialized JSON string for our Dialogflow response.
        result = self.app(environ, start_response)
        try:
            if not headers:
                raise AssertionError("start_response() not called by WSGI app")

            output = json.loads(b"".join(result))
            if not headers[0].startswith("2"):
                raise AssertionError("Non-2xx from app: hdrs={}, body={}".format(headers, output))

            # API Gateway expects Status code, headers and Body
            return {'statusCode': 200, 'headers': {'Content-Type': 'application/json'}, 'body': json.dumps(output)}

        finally:
            # Per the WSGI spec, we need to invoke the close method if it
            # is implemented on the result object.
            if hasattr(result, 'close'):
                result.close()

    def _context_satified(self, view_func):
        met = []
        requires = list(self._func_contexts[view_func])
        recieved_contexts = [c['name'] for c in self.context_in]

        for req_context in requires:
            if req_context in recieved_contexts:
                met.append(req_context)

        if set(met) == set(requires) and len(requires) <= len(recieved_contexts):
            return True

    @property
    def _context_views(self):
        """Returns view functions for which the context requirements are met"""
        possible_views = []

        for func in self._func_contexts:
            if self._context_satified(func):
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
            _errordump('possible views: {}'.format(self._context_views))
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

    def _map_params_to_view_args(self, arg_names):  # TODO map to correct name
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
