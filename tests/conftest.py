import os
import json
import pytest
from flask import Flask
import flask_assistant
from flask_assistant import Assistant, ask, tell, context_manager as manager
from flask_assistant.utils import get_assistant
from flask_assistant.manager import ContextManager
from tests.helpers import build_payload


PROJECT_ROOT = os.path.abspath(os.path.join(flask_assistant.__file__, "../.."))


@pytest.fixture(autouse=True)
def no_requests(monkeypatch):
    monkeypatch.delattr("requests.sessions.Session.request")


## Samples ##
@pytest.fixture(scope="session")
def hello_world_assist():
    filename = os.path.join(PROJECT_ROOT, "samples", "hello_world", "webhook.py")
    return get_assistant(filename)


## Basic Assistant to test Intent matching ##
@pytest.fixture(scope="session")
def simple_assist():
    app = Flask(__name__)
    assist = Assistant(app, project_id="test-project-id")

    @assist.action("TestIntent")
    def test_1():
        speech = "Message1"
        return ask(speech)

    @assist.action("test_intent_2")
    def test_2():
        speech = "Message2"
        return ask(speech)

    @assist.action("test intent 3")
    def test_3():
        speech = "Message3"
        return ask(speech)

    @assist.action("TestIntent")
    def test_action():
        speech = "Message1"
        return ask(speech)

    return assist


@pytest.fixture(scope="session")
def simple_client(simple_assist):
    return simple_assist.app.test_client()


@pytest.fixture(params=["TestIntent", "test_intent_2", "test intent 3"])
def intent_payload(request):
    return build_payload(intent=request.param)


## Assistant to test contexts ##
@pytest.fixture(scope="session")
def context_assist():

    app = Flask(__name__)
    assist = Assistant(app, project_id="test-project-id")

    @assist.action("AddContext")
    def add_context():
        speech = "Adding context to context_out"
        manager.add("SampleContext")
        return ask(speech)

    @assist.context("SampleContext")
    @assist.action("ContextRequired")
    def context_dependent_action():
        speech = "Matched because SampleContext was active"
        return ask(speech)

    @assist.action("ContextRequired")
    def action_func():
        speech = "Message"
        return ask(speech)

    @assist.action("ContextNotRequired")
    def context_independent_actions():
        speech = "No context required"
        return ask(speech)

    return assist


## Assistant to test docs examples ##
@pytest.fixture(scope="session")
def docs_assist():

    app = Flask(__name__)
    assist = Assistant(app)

    @assist.action("give-diet")
    def set_user_diet(diet):
        speech = "Are you trying to make food or get food?"
        manager.add(diet)
        return ask(speech)

    @assist.context("vegetarian")
    @assist.action("get-food")
    def suggest_food():
        return tell("There's a farmers market tonight.")

    @assist.context("carnivore")
    @assist.action("get-food")
    def suggest_food():
        return tell("Bob's BBQ has some great tri tip")

    @assist.context("broke")
    @assist.action("get-food")
    def suggest_food():
        return tell("Del Taco is open late")

    return assist
