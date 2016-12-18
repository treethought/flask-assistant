from . import logger
from flask import json, Response, make_response
from xml.etree import ElementTree
from pprint import pprint


class _Response(object):
    """docstring for _Response"""

    def __init__(self, speech):

        self._json_default = None
        self._response = {
            'speech': speech,
            'displayText': '',
            'data': {},
            'contextOut': [],
            'source': 'webhook'

        }

    def display_text(self, text):
        self._response['displayText'] = text
        return self

    def context_out(self, context_dict):
        # obj = {"name": name, "lifespan": lifespan, "parameters": parameters}
        self._response['contextOut'].append(context_dict)
        return self

    def add_source(self, source):
        self._response['source'] = source
        return self

    def render_response(self):
        # _dbgdump(self._response)
        pprint(self._response)
        resp = json.dumps(self._response, indent=4)
        resp = make_response(resp)
        resp.headers['Content-Type'] = 'application/json'
        return resp


class statement(_Response):
    def __init__(self, speech):
        super(statement, self).__init__(speech)
        self._response['data'] = {}


def _dbgdump(obj, indent=2, default=None, cls=None):
    msg = json.dumps(obj, indent=indent, default=default, cls=cls)
    logger.debug(msg)
