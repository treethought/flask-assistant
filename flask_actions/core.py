from flask import current_app, json, request as flask_request, _app_ctx_stack
from werkzeug.local import LocalProxy

from functools import wraps, partial
import inspect

from . import logger
from .response import _Response


request = LocalProxy(lambda: current_app._app_ctx_stack.request)
result = LocalProxy(lambda: current_app._app_ctx_stack.result)
contexts = LocalProxy(lambda: current_app._app_ctx_stack.contexts)
metadata = LocalProxy(lambda: current_app._app_ctx_stack.metadata)


class _Field(dict):

    def __init__(self, request_json={}):
        super(_Field, self).__init__(request_json)
        for key, value in request_json.items():
            if isinstance(value, dict):
                value = _Field(value)
            self[key] = value

    def __getattr__(self, attr):
        # converts timestamp str to datetime.datetime object
        if 'timestamp' in attr:
            return aniso8601.parse_datetime(self.get(attr))
        return self.get(attr)

    def __setattr__(self, key, value):
        self.__setitem__(key, value)


class _Request(object):
    """When an intent is triggered,
    API.AI sends data to the service in the form of POST request with
   a body in the format of response to a query.

   https://docs.api.ai/docs/webhook

   format -> https://docs.api.ai/docs/query#response
    """

    def __init__(self, api_request_payload):

        self.payload = api_request_payload


class Agent(object):
    """Central Interface for itneracting with the Google Actions via Api.ai"""

    def __init__(self, app=None, route='/'):

        self.app = app
        self._route = route
        self._intent_view_funcs = {}
        if app is not None:
            self.init_app(app)

    def init_app(self, app):

        if self._route is None:
            raise TypeError("route is a required argument when app is not None")

        app.agent = self

        app.add_url_rule(self._route, view_func=self._flask_view_func, methods=['POST'])


    def intent(self, intent_name):
        def decorator(f):
            self._intent_view_funcs[intent_name] = f

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
        _dbgdump(payload)

        result = None
        intent_name = payload['result']['metadata']['intentName']
        result = self._map_intent_to_view_func(intent_name)()

        if result is not None:
            if isinstance(result, _Response):
                return result.render_response()
            return result
        return "", 400

    def _map_intent_to_view_func(self, intent):
        view_func = self._intent_view_funcs[intent]
        argspec = inspect.getargspec(view_func)
        arg_names = argspec.args
        # arg_values = self._map_params_to_view_args(intent.name, arg_names)
        arg_values = []
        return partial(view_func, *arg_values)

def _dbgdump(obj, indent=2, default=None, cls=None):
    msg = json.dumps(obj, indent=indent, default=default, cls=cls)
    logger.debug(msg)
