import os
import requests
import json

from . import logger
from .models import Intent, Entity


class ApiAi(object):
    """Interface for making and recieving API-AI requests.

    Use the developer access token for managing entities and intents and the client access token for making queries.

    """

    def __init__(self, dev_token=None, client_token=None):

        self._dev_token = dev_token or os.getenv("DEV_ACCESS_TOKEN")
        self._client_token = client_token or os.getenv("CLIENT_ACCESS_TOKEN")
        self.base_url = "https://dialogflow.googleapis.com/v2"

    @property
    def _dev_header(self):
        if self._dev_token is None:
            raise ValueError(
                "No Dialogflow dev_token set.\nTokens must be passed to the Assistant() constructor or set as enviornment variable"
            )
        return {
            "Authorization": "Bearer {}".format(self._dev_token),
            "Content-Type": "application/json",
        }

    @property
    def _client_header(self):
        if self._client_token is None:
            raise ValueError(
                "No Dialogflow client_token set.\nTokens must be passed to Assistant() constructor or set as enviornment variable"
            )
        return {
            "Authorization": "Bearer {}".format(self._client_token),
            "Content-Type": "application/json; charset=utf-8",
        }

    def _intent_uri(self, intent_id=""):
        if intent_id != "":
            intent_id = "/" + intent_id
        return "{}intents{}?v={}".format(self.base_url, intent_id, self.versioning)

    def _entity_uri(self, entity_id=""):
        if entity_id != "":
            entity_id = "/" + entity_id
        return "{}entities{}?v={}".format(self.base_url, entity_id, self.versioning)

    @property
    def _query_uri(self):
        return "{}query?v={}".format(self.base_url, self.versioning)

    def _get(self, endpoint):
        response = requests.get(endpoint, headers=self._dev_header)
        response.raise_for_status
        logger.debug("Response from {}: {}".format(endpoint, response))
        return response.json()

    def _post(self, endpoint, data):
        response = requests.post(endpoint, headers=self._dev_header, data=data)
        response.raise_for_status
        return response.json()

    def _put(self, endpoint, data):
        response = requests.put(endpoint, headers=self._dev_header, data=data)
        response.raise_for_status
        return response.json()

    ## Intents ##

    @property
    def agent_intents(self):
        """Returns a list of intent json objects"""
        endpoint = self._intent_uri()
        intents = self._get(endpoint)  # should be list of dicts
        if isinstance(intents, dict):  # if error: intents = {status: {error}}
            raise Exception(intents["status"])

        return [Intent(intent_json=i) for i in intents]

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

    ## Entities ##

    @property
    def agent_entities(self):
        """Returns a list of intent json objects"""
        endpoint = self._entity_uri()
        entities = self._get(endpoint)  # should be list of dicts
        if isinstance(entities, dict):  # error: entities = {status: {error}}
            raise Exception(entities["status"])

        return [Entity(entity_json=i) for i in entities if isinstance(i, dict)]

    def get_entity(self, entity_id):
        endpoint = self._entity_uri(entity_id=entity_id)
        return self._get(endpoint)

    def post_entity(self, entity_json):
        endpoint = self._entity_uri()
        return self._post(endpoint, data=entity_json)

    def put_entity(self, entity_id, entity_json):
        endpoint = self._entity_uri(entity_id)
        return self._put(endpoint, data=entity_json)

    ## Querying ##
    def post_query(self, query, sessionID=None):
        data = {
            "query": query,
            "sessionId": sessionID or "123",
            "lang": "en",
            "contexts": [],
        }

        data = json.dumps(data)

        response = requests.post(
            self._query_uri, headers=self._client_header, data=data
        )
        response.raise_for_status
        return response
