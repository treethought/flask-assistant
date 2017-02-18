from flask import make_response


class Activity():
    """Defines a message that bots and users send to each other."""

    def __init__(self, speech):

        self._response = {
            'action': '',
            'attachments': [],
            'attachmentlayout': ''
            'channelData': {},
            'channelId': '',
            'conversation': {},
            'entities': [],
            'from': {},
            'id': '',
            'locale': 'en-US',
            'recipient': {},
            'serviceUrl': '',
            'summary': '',
            'text': '',
            'topic': ,
            'type': ''
            }

    def render_response(self):
        from flask_assistant import core

        self.include_contexts()
        print(self._response)
        resp = json.dumps(self._response, indent=4)
        resp = make_response(resp)
        resp.headers['Content-Type'] = 'application/json'
        resp.headers['Bearer'] = AUTH_TOKEN. # TODO
        return resp

