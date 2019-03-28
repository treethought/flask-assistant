import inspect
import sys
import os
from functools import wraps, partial

import aniso8601
from flask import current_app, json, request as flask_request, _app_ctx_stack
from werkzeug.local import LocalProxy

from flask_assistant import logger
from flask_assistant.response import _Response
from flask_assistant.manager import ContextManager, parse_context_name
from api_ai.api import ApiAi
from io import StringIO


def find_assistant():  # Taken from Flask-ask courtesy of @voutilad
    """
    Find our instance of Assistant, navigating Local's and possible blueprints.

    Note: This only supports returning a reference to the first instance
    of Assistant found.
    """
    if hasattr(current_app, "assist"):
        return getattr(current_app, "assist")
    else:
        if hasattr(current_app, "blueprints"):
            blueprints = getattr(current_app, "blueprints")
            for blueprint_name in blueprints:
                if hasattr(blueprints[blueprint_name], "assist"):
                    return getattr(blueprints[blueprint_name], "assist")


request = LocalProxy(lambda: find_assistant().request)
intent = LocalProxy(lambda: find_assistant().intent)
access_token = LocalProxy(lambda: find_assistant().access_token)
context_in = LocalProxy(lambda: find_assistant().context_in)
context_manager = LocalProxy(lambda: find_assistant().context_manager)
convert_errors = LocalProxy(lambda: find_assistant().convert_errors)
session_id = LocalProxy(lambda: find_assistant().session_id)
user = LocalProxy(lambda: find_assistant().user)
storage = LocalProxy(lambda: find_assistant().storage)

# Converter shorthands for commonly used system entities
_converter_shorthands = {
    "date": aniso8601.parse_date,  # Returns date
    "date-period": aniso8601.parse_interval,  # Returns (date, date)
    "time": aniso8601.parse_time,  # Returns time
}


class Assistant(object):
    """Central Interface for creating a Dialogflow webhook.

    The Assistant object routes requests to :func:`action` decorated functions.

    The assistant object maps requests received from an Dialogflow agent to Intent-specific view functions.
    The view_functions can be properly matched depending on required parameters and contexts.
    These requests originate from Google Actions and are sent to the Assistant object
    through Dialogflow's infrastructure.


    Keyword Arguments:
        app {Flask object} -- App instance - created with Flask(__name__) (default: {None})
        blueprint {Flask Blueprint} -- Flask Blueprint instance to initialize (Default: {None})
        route {str} -- entry point to which initial Alexa Requests are forwarded (default: {None})
        project_id {str} -- Google Cloud Project ID, required to manage contexts from flask-assistant
        dev_token {str} - Dialogflow dev access token used to register and retrieve agent resources
        client_token {str} - Dialogflow client access token required for querying agent
    """

    def __init__(
        self,
        app=None,
        blueprint=None,
        route=None,
        project_id=None,
        dev_token=None,
        client_token=None,
    ):

        self.app = app
        self.blueprint = blueprint
        self._route = route
        self.project_id = project_id
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
            self._route = "/"

        if app is not None:
            self.init_app(app)
        elif blueprint is not None:
            self.init_blueprint(blueprint)
        else:
            raise ValueError(
                "Assistant object must be intialized with either an app or blueprint"
            )

        if project_id is None:
            import warnings

            warnings.warn(
                """\nGoogle Cloud Project ID is required to manage contexts using flask-assistant\n
                Please initialize the Assistant object with a project ID
                assist = Assistant(app, project_id='YOUR_PROJECT_ID")""",
                stacklevel=2,
            )

    def init_app(self, app):

        if self._route is None:
            raise TypeError("route is a required argument when app is not None")

        app.assist = self
        app.add_url_rule(
            self._route, view_func=self._flask_assitant_view_func, methods=["POST"]
        )

    # Taken from Flask-ask courtesy of @voutilad
    def init_blueprint(self, blueprint, path="templates.yaml"):
        """Initialize a Flask Blueprint, similar to init_app, but without the access
        to the application config.

        Keyword Arguments:
            blueprint {Flask Blueprint} -- Flask Blueprint instance to initialize
                                        (Default: {None})
            path {str} -- path to templates yaml file, relative to Blueprint
                      (Default: {'templates.yaml'})
        """
        if self._route is not None:
            raise TypeError("route cannot be set when using blueprints!")

        # we need to tuck our reference to this Assistant instance
        # into the blueprint object and find it later!
        blueprint.assist = self

        # BlueprintSetupState.add_url_rule gets called underneath the covers and
        # concats the rule string, so we should set to an empty string to allow
        # Blueprint('blueprint_api', __name__, url_prefix="/assist") to result in
        # exposing the rule at "/assist" and not "/assist/".
        blueprint.add_url_rule(
            "", view_func=self._flask_assitant_view_func, methods=["POST"]
        )
        # blueprint.jinja_loader = ChoiceLoader([YamlLoader(blueprint, path)])

    @property
    def request(self):
        """Local Proxy refering to the request JSON recieved from Dialogflow"""
        return getattr(_app_ctx_stack.top, "_assist_request", None)

    @request.setter
    def request(self, value):
        _app_ctx_stack.top._assist_request = value

    @property
    def intent(self):
        """Local Proxy refering to the name of the intent contained in the Dialogflow request"""
        return getattr(_app_ctx_stack.top, "_assist_intent", None)

    @intent.setter
    def intent(self, value):
        _app_ctx_stack.top._assist_intent = value

    @property
    def access_token(self):
        """Local proxy referring to the OAuth token for linked accounts."""
        return getattr(_app_ctx_stack.top, "_assist_access_token", None)

    @access_token.setter
    def access_token(self, value):
        _app_ctx_stack.top._assist_access_token = value

    @property
    def context_in(self):
        """Local Proxy refering to context objects contained within current session"""
        return getattr(_app_ctx_stack.top, "_assist_context_in", [])

    @context_in.setter
    def context_in(self, value):
        _app_ctx_stack.top._assist_context_in = value

    @property
    def context_manager(self):
        """LocalProxy refering to the app's instance of the  :class: `ContextManager`.

        Interface for adding and accessing contexts and their parameters
        """
        return getattr(
            _app_ctx_stack.top, "_assist_context_manager", ContextManager(self)
        )

    @context_manager.setter
    def context_manager(self, value):
        _app_ctx_stack.top._assist_context_manager = value

    @property
    def convert_errors(self):
        return getattr(_app_ctx_stack.top, "_assistant_convert_errors", None)

    @convert_errors.setter
    def convert_errors(self, value):
        _app_ctx_stack.top._assistant_convert_errors = value

    @property
    def session_id(self):
        return getattr(_app_ctx_stack.top, "_assist_session_id", None)

    @session_id.setter
    def session_id(self, value):
        _app_ctx_stack.top._assist_session_id = value

    @property
    def user(self):
        return getattr(_app_ctx_stack.top, "_assist_user", {})

    @user.setter
    def user(self, value):
        storage_data = value.get("userStorage", {})

        if not isinstance(storage_data, dict):
            storage_data = json.loads(storage_data)

        value["userStorage"] = storage_data

        _app_ctx_stack.top._assist_user = value
        _app_ctx_stack.top._assist_storage = storage_data

    @property
    def storage(self):
        return self.user.get("userStorage", {})

    @storage.setter
    def storage(self, value):
        if not isintance(value, dict):
            raise TypeError("Storage must be a dictionary")

        self.user["userStorage"] = value

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

    def action(
        self,
        intent_name,
        is_fallback=False,
        mapping={},
        convert={},
        default={},
        with_context=[],
        events=[],
        *args,
        **kw
    ):
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

    def _dialogflow_request(self, verify=True):
        raw_body = flask_request.data
        _dialogflow_request_payload = json.loads(raw_body)

        return _dialogflow_request_payload

    def _dump_request(self,):
        summary = {
            "Intent": self.intent,
            "Incoming Contexts": [c.name for c in self.context_manager.active],
            "Source": self.request["originalDetectIntentRequest"].get("source"),
            "Missing Params": self._missing_params,
            "Received Params": self.request["queryResult"]["parameters"],
        }
        msg = "Request: " + json.dumps(summary, indent=2, sort_keys=True)
        logger.info(msg)

    def _dump_result(self, view_func, result):
        summary = {
            "Intent": self.intent,
            "Outgoing Contexts": [c.name for c in self.context_manager.active],
            "Matched Action": view_func.__name__,
            "Response Speech": result._speech,
        }
        msg = "Result: " + json.dumps(summary, indent=2, sort_keys=True)
        logger.info(msg)

    def _parse_session_id(self):
        return self.request["session"].split("/sessions/")[1]

    def _flask_assitant_view_func(self, nlp_result=None, *args, **kwargs):
        if nlp_result:  # pass API query result directly
            self.request = nlp_result
        else:  # called as webhook
            self.request = self._dialogflow_request(verify=False)

        logger.debug(json.dumps(self.request, indent=2))

        try:
            self.intent = self.request["queryResult"]["intent"]["displayName"]
            self.context_in = self.request["queryResult"].get("outputContexts", [])
            self.session_id = self._parse_session_id()
            assert self.session_id is not None
        except KeyError:
            raise DeprecationWarning(
                """It appears your agent is still using the Dialogflow V1 API,
                please update to V2 in the Dialogflow console."""
            )

        # update context_manager's assist reference
        # TODO: acces context_manager from assist, instead of own object
        self.context_manager._assist = self

        original_request = self.request.get("originalDetectIntentRequest")

        if original_request:
            payload = original_request.get("payload")
            if payload and payload.get("user"):
                self.user = original_request["payload"]["user"]

        # Get access token from request
        if original_request and original_request.get("user"):
            self.access_token = original_request["user"].get("accessToken")

        self._update_contexts()
        self._dump_request()

        view_func = self._match_view_func()
        if view_func is None:
            logger.error("Failed to match an action function")
            return "", 400

        logger.info("Matched action function: {}".format(view_func.__name__))
        result = self._map_intent_to_view_func(view_func)()

        if result is not None:
            if isinstance(result, _Response):
                self._dump_result(view_func, result)
                resp = result.render_response()
                return resp
            return result
        logger.error("Action func returned empty response")
        return "", 400

    def _update_contexts(self):
        temp = self.context_manager
        temp.update(self.context_in)
        self.context_manager = temp

    def _match_view_func(self):
        view_func = None

        intent_actions = self._intent_action_funcs.get(self.intent, [])
        if len(intent_actions) == 0:
            logger.critical(
                "No action funcs defined for intent: {}".format(self.intent)
            )
            return view_func

        if self.has_live_context():
            view_func = self._choose_context_view()

        if not view_func and self._missing_params:
            prompts = self._intent_prompts.get(self.intent)
            if prompts:
                param_choice = self._missing_params.pop()
                view_func = prompts.get(param_choice)
                logger.debug(
                    "Matching prompt func {} for missing param {}".format(
                        view_func.__name__, param_choice
                    )
                )

        if not view_func and len(intent_actions) == 1:
            view_func = self._intent_action_funcs[self.intent][0]

        # TODO: Do not match func if context not satisfied

        if not view_func and len(intent_actions) > 1:
            view_func = intent_actions[0]
            msg = "Multiple actions defined but no context was applied, will use first action func"
            logger.warning(msg)

        return view_func

    def has_live_context(self):
        for context in self.context_in:
            # lifespanCount appears to be missing if context expired
            if context.get("lifespanCount", 0) > 0:
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
        enc, esc = sys.getfilesystemencoding(), "surrogateescape"

        def unicode_to_wsgi(u):
            return u.encode(enc, esc).decode("iso-8859-1")

        # Create a WSGI-compatible environ that can be passed to the
        # application. It is loaded with the OS environment variables,
        # mandatory CGI-like variables, as well as the mandatory WSGI
        # variables.
        environ = {k: unicode_to_wsgi(v) for k, v in os.environ.items()}
        environ["REQUEST_METHOD"] = "POST"
        environ["PATH_INFO"] = "/"
        environ["SERVER_NAME"] = "AWS-Lambda"
        environ["SERVER_PORT"] = "80"
        environ["SERVER_PROTOCOL"] = "HTTP/1.0"
        environ["wsgi.version"] = (1, 0)
        environ["wsgi.url_scheme"] = "http"
        environ["wsgi.errors"] = sys.stderr
        environ["wsgi.multithread"] = False
        environ["wsgi.multiprocess"] = False
        environ["wsgi.run_once"] = True

        # Convert the event provided by the AWS Lambda handler to a JSON
        # string that can be read as the body of a HTTP POST request.
        body = event["body"]
        environ["CONTENT_TYPE"] = "application/json"
        environ["CONTENT_LENGTH"] = len(body)
        environ["wsgi.input"] = StringIO(body)

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
                raise AssertionError(
                    "Non-2xx from app: hdrs={}, body={}".format(headers, output)
                )

            # API Gateway expects Status code, headers and Body
            return {
                "statusCode": 200,
                "headers": {"Content-Type": "application/json"},
                "body": json.dumps(output),
            }

        finally:
            # Per the WSGI spec, we need to invoke the close method if it
            # is implemented on the result object.
            if hasattr(result, "close"):
                result.close()

    def _context_satified(self, view_func):
        met = []

        required_names = list(self._func_contexts[view_func])
        recieved_context_names = [parse_context_name(c) for c in self.context_in]

        for req_context in required_names:
            if req_context in recieved_context_names:
                met.append(req_context)

        if set(met) == set(required_names):
            if len(required_names) <= len(recieved_context_names):
                return True

    @property
    def _context_views(self):
        """Returns view functions for which the context requirements are met"""
        possible_views = []

        for func in self._func_contexts:
            if self._context_satified(func):
                logger.debug("{} context conditions satisified".format(func.__name__))
                possible_views.append(func)
        return possible_views

    def _choose_context_view(self):
        choice = None
        for view in self._context_views:
            if view in self._intent_action_funcs[self.intent]:
                logger.debug(
                    "Matched {} based on active contexts".format(view.__name__)
                )
                choice = view
        if choice:
            return choice
        else:
            active_contexts = [c.name for c in self.context_manager.active]
            intent_actions = [
                f.__name__ for f in self._intent_action_funcs[self.intent]
            ]
            msg = "No {} action func matched based on active contexts"

            logger.debug(msg)

    @property
    def _missing_params(self):  # TODO: fill missing slot from default\

        params = self.request["queryResult"]["parameters"]
        missing = []
        for p_name in params:
            if params[p_name] == "":
                missing.append(p_name)

        return missing

    def _func_args(self, f):
        try:
            argspec = inspect.getfullargspec(f)

        except AttributeError:  # for python2
            argspec = inspect.getargspec(f)

        return argspec.args

    def _map_intent_to_view_func(self, view_func):
        arg_names = self._func_args(view_func)
        arg_values = self._map_params_to_view_args(arg_names)
        return partial(view_func, *arg_values)

    def _map_params_to_view_args(self, arg_names):  # TODO map to correct name
        arg_values = []
        mapping = self._intent_mappings.get(self.intent)
        convert = self._intent_converts.get(self.intent)
        params = self.request["queryResult"]["parameters"]

        convert_errors = {}

        for arg_name in arg_names:
            entity_mapping = mapping.get(arg_name, arg_name)
            # param name cant have '.',
            # so when registered, the sys. is stripped,
            # and must be stripped when looking up in request
            mapped_param_name = entity_mapping.replace("sys.", "")
            value = params.get(
                mapped_param_name
            )  # params declared in GUI present in request

            if not value:  # params not declared, so must look in contexts
                value = self._map_arg_from_context(arg_name)
            elif arg_name in convert:
                # Apply parameter conversion
                shorthand_or_function = convert[arg_name]
                if shorthand_or_function in _converter_shorthands:
                    convert_func = _converter_shorthands[shorthand_or_function]
                else:
                    convert_func = shorthand_or_function
                try:
                    value = convert_func(value)
                except Exception as exc:
                    convert_errors[arg_name] = exc
            arg_values.append(value)

        self.convert_errors = convert_errors
        return arg_values

    def _map_arg_from_context(self, arg_name):
        for context_obj in self.context_in:
            if arg_name in context_obj["parameters"]:
                logger.debug(
                    "Retrieved {} param value from {} context".format(
                        arg_name, context_obj["name"]
                    )
                )
                return context_obj["parameters"][arg_name]
