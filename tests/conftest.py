import os
import json
import pytest
from flask import Flask
import flask_assistant
from flask_assistant import Assistant, ask, tell
from flask_assistant.utils import get_assistant
from tests.helpers import build_payload


PROJECT_ROOT = os.path.abspath(os.path.join(flask_assistant.__file__, '../..'))


@pytest.fixture(autouse=True)
def no_requests(monkeypatch):
    monkeypatch.delattr("requests.sessions.Session.request")


@pytest.fixture(scope='session')
def hello_world_assist():
    filename = os.path.join(PROJECT_ROOT, 'samples', 'hello_world', 'webhook.py')
    return get_assistant(filename)




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

    @assist.context('TestContext', 'SecondContext')
    @assist.action('TestIntent')
    def test_action():
        speech = 'Message1'
        return ask(speech)

    return assist


@pytest.fixture(scope='session')
def app_client(assist):
    return assist.app.test_client()


@pytest.fixture(params=['TestIntent', 'test_intent_2', 'test intent 3'])
def intent_payload(request):
    return build_payload(intent=request.param)




