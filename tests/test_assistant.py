import pytest

from flask import Flask
from flask_assistant import Assistant, ask, context_manager as manager
from tests.helpers import build_payload, get_query_response

@pytest.fixture(scope='session')
def assist():
    app = Flask(__name__)
    assist = Assistant(app)

    @assist.action('TestIntent')
    def test_1():
        speech = 'Message1'
        return ask(speech)

    @assist.action('test_intent_2')
    def test_2():
        speech = 'Message2'
        return ask(speech)

    @assist.action('test intent 3')
    def test_3():
        speech = 'Message3'
        return ask(speech)

    @assist.action('TestIntent')
    def test_action():
        speech = 'Message1'
        return ask(speech)

    return assist


@pytest.fixture(scope='session')
def context_assist():

    app = Flask(__name__)
    assist = Assistant(app)
    
    @assist.action('AddContext')
    def add_context():
        speech = 'Adding context to context_out'
        manager.add('SampleContext')
        return ask(speech)

    @assist.context('SampleContext')
    @assist.action('ContextRequired')
    def context_dependent_action():
        speech = 'Matched because SampleContext was active'
        return ask(speech)

    @assist.action('ContextNotRequired')
    def context_independent_actions():
        speech = 'No context required'
        return ask(speech)

    return assist


@pytest.fixture(scope='session')
def app_client(assist):
    return assist.app.test_client()


@pytest.fixture(params=['TestIntent', 'test_intent_2', 'test intent 3'])
def intent_payload(request):
    return build_payload(intent=request.param)

def test_intents_with_different_formatting(app_client, intent_payload):

    resp = get_query_response(app_client, intent_payload)
    assert 'Message' in resp['speech']

    resp = app_client.post('/', data=intent_payload)
    assert resp.status_code == 200

    assert b'Message' in resp.data


def test_adding_context(context_assist):
    client = context_assist.app.test_client()
    payload = build_payload('AddContext')
    resp = get_query_response(client, payload)
    context_obj = {'lifespan': 5, 'name': 'SampleContext', 'parameters': {}}
    assert context_obj in resp['contextOut']

# def test_need_context_to_match_action(context_assist):
#     client = context_assist.app.test_client()
#     payload = build_payload('ContextRequired')
#     resp = get_query_response(client, payload)
#     assert 'Matched because SampleContext was active' not in resp['speech']


