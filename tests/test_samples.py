import os
import json
from requests import post
from pprint import pprint
import pytest
from flask_assistant.utils import get_assistant


def build_payload(intent, params={}, contexts={}, action='test_action', query='test query'):

    return json.dumps({
        "id": "8ea2d357-10c0-40d1-b1dc-e109cd714f67",
        "timestamp": "2017-06-26T22:43:14.935Z",
        "lang": "en",
        "result": {
            "action": action,
            "actionIncomplete": False,
            "contexts": contexts,
            "fulfillment": {
                "messages": [],
                "speech": ""
            },
            "metadata": {
                "intentId": "some-intent-id",
                "intentName": intent,
                "webhookForSlotFillingUsed": "false",
                "webhookUsed": "true"
            },
            "parameters": params,
            "resolvedQuery": query,
            "score": 1.0,
            "source": "agent",
            "speech": ""
        },
        "status": {
            "code": 200,
            "errorType": "success"
        },
        "sessionId": "c24d9cfe-21c9-4fc0-a5eb-1a2ee1fec29c"
    })


# def test_intents_produce_correct_response(app_client, intent_payload):
#     resp = app_client.post('/', data=intent_payload)
#     assert resp.status_code == 200
#     pprint(resp.data, indent=3)
#     assert b'Message' in resp.data



def get_query_response(client, payload):
    resp = client.post('/', data=payload)
    assert resp.status_code == 200
    return json.loads(resp.data)


def test_hello_world_greeting(hello_world_assist):
    client = hello_world_assist.app.test_client()
    payload = build_payload('greeting')
    resp = get_query_response(client, payload)
    assert 'male or female' in resp['speech']

def test_hello_world_give_gender(hello_world_assist):
    client = hello_world_assist.app.test_client()
    payload = build_payload('user-gives-gender', params={'gender': 'male'})
    resp = get_query_response(client, payload)
    assert 'Sup bro' in resp['speech']
    assert 'What is your favorite color?' in resp['speech']

def test_hello_world_give_color(hello_world_assist):
    client = hello_world_assist.app.test_client()
    payload = build_payload('give-color', params={'color': 'blue'})
    resp = get_query_response(client, payload)

    assert 'Ok, blue is an okay' in resp['speech']



















