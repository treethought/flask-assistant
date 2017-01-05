from . import logger
from . import core
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

    def add_context(self, *context_dicts):
        for context in context_dicts:
            self._response['contextOut'].append(context.serialize)
        return self

    def add_source(self, source):
        self._response['source'] = source
        return self

    def render_response(self):
        # _dbgdump(self._response)
        core._dbgdump(self._response)
        resp = json.dumps(self._response, indent=4)
        resp = make_response(resp)
        resp.headers['Content-Type'] = 'application/json'
        return resp


class statement(_Response):
    def __init__(self, speech):
        super(statement, self).__init__(speech)
        self._response['data'] = {}



