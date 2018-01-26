from flask import json, make_response


class _ApiAiResponse(object):
    """Base class for all response objects. Returns a JSON object

    https://api.ai/docs/fulfillment#response
    https://api.ai/docs/reference/agent/query#response

    """

    def __init__(self, speech, display_text=None, followup_event=None):

        if display_text is None:
            display_text = speech

        if followup_event is None:
            followup_event = dict()

        self.speech = speech
        self.display_text = display_text
        self.followup_event = followup_event

        self._response = {
            'speech': self.speech,
            'displayText': self.display_text,
            'data': {},
            'contextOut': [],
            'source': 'webhook',
            'followupEvent': self.followup_event,
            # 'messages': self._messages,
        }


    def _include_contexts(self):
        from flask_assistant import core

        for context in core.context_manager.active:
            self._response['contextOut'].append(context.serialize)

    def render_response(self):
        from flask_assistant import core

        self._include_contexts()
        core._dbgdump(self._response)
        resp = json.dumps(self._response, indent=4)
        resp = make_response(resp)
        resp.headers['Content-type'] = 'application/json'
        return resp
