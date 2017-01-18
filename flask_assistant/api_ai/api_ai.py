import os
import requests
import datetime
from flask import make_response
import json


class ApiAi(object):
    """Interface for making and recieving API-AI requests.

    Use the developer access token for managing entities and intents and the client access token for making queries.

    """

    def __init__(self, assistant, dev_token=os.environ.get('DEV_ACCESS_TOKEN')):

        self.assist = assistant
        self._dev_token = dev_token
        self.versioning = '20161213'
        self.base_url = 'https://api.api.ai/v1/'

    @property
    def _dev_header(self):
        return {'Authorization': 'Bearer {}'.format(self._dev_token),
                'Content-Type': 'application/json'}

    def _intent_uri(self, intent_id=''):
        if intent_id != '':
            intent_id = '/' + intent_id
        return '{}intents{}?v={}'.format(self.base_url, intent_id, self.versioning)

    def _get(self, endpoint):
        response = requests.get(endpoint, headers=self._dev_header)
        response.raise_for_status
        return response.json()

    def _post(self, endpoint, data):
        response = requests.post(endpoint, headers=self._dev_header, data=data)
        response.raise_for_status
        return response.json()

    def _put(self, endpoint, data):
        response = requests.put(endpoint, headers=self._dev_header, data=data)
        response.raise_for_status
        return response.json()

    @property
    def get_agent_intents(self):
        """Returns a list of intent json objects"""
        endpoint = self._intent_uri()
        intents = [_Field(i) for i in self._get(endpoint)]
        return intents

    def get_intent(self, intent_id):
        """Returns the intent object with the given intent_id"""
        endpoint = self._intent_uri(intent_id=intent_id)
        return self._get(endpoint)

    def post_intent(self, intent_json):
        """Sends post request to create a new intent"""
        endpoint = self._intent_uri()
        return self._post(endpoint, data=intent_json)

    def put_intent(self, intent_id, intent_json):
        """Send a put request to update the intent with intent_id"""
        endpoint = self._intent_uri(intent_id)
        return self._put(endpoint, intent_json)


if __name__ == '__main__':

    from flask import Flask
    from flask_assistant import Assistant
    from samples.pizza_contexts.agent import assist

    intent = {
        "name": "change appliance state",
        "auto": True,
        "contexts": [],
        "templates": [
            "turn @state:state the @appliance:appliance ",
            "switch the @appliance:appliance @state:state "
        ],
        "userSays": [
            {
                "data": [
                    {
                        "text": "turn "
                    },
                    {
                        "text": "on",
                        "alias": "state",
                        "meta": "@state"
                    },
                    {
                        "text": " the "
                    },
                    {
                        "text": "kitchen lights",
                        "alias": "appliance",
                        "meta": "@appliance"
                    }
                ],
                "isTemplate": False,
                "count": 0
            },
            {
                "data": [
                    {
                        "text": "switch the "
                    },
                    {
                        "text": "heating",
                        "alias": "appliance",
                        "meta": "@appliance"
                    },
                    {
                        "text": " "
                    },
                    {
                        "text": "off",
                        "alias": "state",
                        "meta": "@state"
                    }
                ],
                "isTemplate": False,
                "count": 0
            }
        ],
        "responses": [
            {
                "resetContexts": False,
                "action": "set-appliance",
                "affectedContexts": [
                    {
                        "name": "house",
                        "lifespan": 10
                    }
                ],
                "parameters": [
                    {
                        "dataType": "@appliance",
                        "name": "appliance",
                        "value": "\$appliance"
                    },
                    {
                        "dataType": "@state",
                        "name": "state",
                        "value": "\$state"
                    }
                ],
                "speech": "Turning the \$appliance \$state\!"
            }
        ],
        "priority": 500000
    }

    app = Flask(__name__)
    ass = Assistant(app)
    a = ApiAi(ass)

    print(a.post_intent(json.dumps(intent)))
