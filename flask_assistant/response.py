from . import logger
from . import core
from flask import json, Response, make_response
from xml.etree import ElementTree


class _Response(object):
    """docstring for _Response"""

    def __init__(self, speech):

        self._json_default = None
        self._response = {
            'speech': speech,
            'displayText': '',
            'data': {
                "google": {
                    "expect_user_response": True,
                    "is_ssml": True,
                    "permissions_request": None,
                }
            },
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

    def get_permission(self, permissions, reason=None):
        if not reason:
            reason = "I need permission to use your info from google."

        self._response['data']["permissions_request"] = {
            "opt_context": reason,
            "permissions": permissions
        },

    def include_contexts(self):
        for context in core.context_manager.active:
            self._response['contextOut'].append(context.serialize)


    def render_response(self):
        self.include_contexts()
        core._dbgdump(self._response)
        resp = json.dumps(self._response, indent=4)
        resp = make_response(resp)
        resp.headers['Content-Type'] = 'application/json'
        return resp


class tell(_Response):
    def __init__(self, speech):
        super(tell, self).__init__(sepeech)
        self._response['data']['google']['expect_user_response'] = False


class ask(_Response):
    def __init__(self, speech):
        super(ask, self).__init__(speech)
        self._response['data']['google']['expect_user_response'] = True

    def reprompt(self, prompt):
        self._response['data']['google']['no_input_prompts'] = [{'text_to_speech': prompt}]
