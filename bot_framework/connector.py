import os
import requests

from flask import json, make_response


from flask_assistant.core import request, _dbgdump


SERVICE_ENDPOINTS = {
    'emulator': os.getenv('EMULATOR_URL', default='https://4bf26eac.ngrok.io/v3/'),
    'botframework': 'https://api.botframework.com/v3/',
    'skype': 'https://smba.trafficmanager.net/apis/v3/'
}


class BotConnector():
    """Sends messages to the Bot Connector service"""

    def __init__(self):

        self._app_id = os.getenv('MICROSOFT_APP_ID')
        self._app_pw = os.getenv('MICROSOFT_APP_PASSWORD')
        self._service = os.getenv('SERVICE')
        self._token_url = 'https://login.microsoftonline.com/common/oauth2/v2.0/token'
        self._token = None
        self._activity = {}

    @property
    def token(self):
        if not self._token:
            return self._get_access_token()
        return self._token

    @property
    def auth_header(self):
        return {'Authorization': 'Bearer {}'.format(self.token),
                'Content-Type': 'application/json'}

    def _get_access_token(self):
        body = {
            'grant_type': 'client_credentials',
            'client_id': self._app_id,
            'client_secret': self._app_pw,
            'scope': 'https://api.botframework.com/.default'
        }
        print('getting access token')
        resp = requests.post(self._token_url, data=body)
        resp.raise_for_status
        return resp.json()['access_token']

    def verify_request(self, request):  # TODO
        # jwt_token=request.headers[]
        pass

    @property
    def base_url(self):
        return SERVICE_ENDPOINTS[self._service]

    @property
    def conversation_id(self):
        return request['conversation']['id']

    @property
    def activity_id(self):
        return request['id']

    @property
    def conversations_uri(self):
        return self.base_url + 'conversations/'

    def authorize_ping(self):
        return 202

    @property
    def activity_data(self):
        return json.dumps(self._activity)

    def build_reply_from_request(self):

        self._activity['channelId'] = request['channelId']
        self._activity['channelData'] = request.get('channelData')
        self._activity['conversation'] = request['conversation']
        self._activity['from'] = request['recipient']
        self._activity['locale'] = request.get('locale')
        self._activity['recipient'] = request['from']
        self._activity['replyToId'] = request['id']
        self._activity['type'] = 'message'
        return self._activity

    # for basic attachments, not rich cards
    # rich cards would have a content property and no url
    def add_attachment(self, content_url, name=None, thumbnail_url=None):

        attachment = {
            'contentType': 'image',
            'contentUrl': content_url,
            'name': name,
            'thumbnailUrl': thumbnail_url
        }

        if not self._activity.get('attachments'):
            self._activity['attachments'] = []
        self._activity['attachments'].append(attachment)
        return self


class reply(BotConnector):
    """Sends a message type Activity in response to an Activity the bot received"""

    def __init__(self, message):
        super().__init__()

        self.build_reply_from_request()

        self._activity['text'] = message

    def send(self):
        endpoint = self.conversations_uri + self.conversation_id + '/activities/' + self.activity_id
        _dbgdump('Sending Activity:')
        _dbgdump(self._activity)

        resp = requests.post(endpoint, data=self.activity_data, headers=self.auth_header)
        resp.raise_for_status
        _dbgdump(resp.status_code)

        return (resp.text, resp.status_code, resp.headers.items())
