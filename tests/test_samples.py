from flask_assistant.utils import get_assistant
from tests.helpers import build_payload, get_query_response




def test_hello_world_greeting(hello_world_assist):
    client = hello_world_assist.app.test_client()
    payload = build_payload('greeting')
    resp = get_query_response(client, payload)
    assert 'male or female' in resp['speech']

def test_hello_world_give_gender(hello_world_assist):
    client = hello_world_assist.app.test_client()
    payload = build_payload('give-gender', params={'gender': 'male'})
    resp = get_query_response(client, payload)
    assert 'Sup bro' in resp['speech']
    assert 'What is your favorite color?' in resp['speech']

def test_hello_world_give_color(hello_world_assist):
    client = hello_world_assist.app.test_client()
    payload = build_payload('give-color', params={'color': 'blue'})
    resp = get_query_response(client, payload)

    assert 'Ok, blue is an okay' in resp['speech']




















