import pytest
from flask import Flask
from flask_assistant import Assistant, ask, context_manager as manager
from injector import Module, Injector, provider, singleton, inject
from tests.helpers import build_payload, get_query_response

class AppModule(Module):
    @provider
    @singleton
    def provide_str(self) -> str:
        return 'TEST INJECTED'

    @provider
    @singleton
    def provide_int(self) -> int:
        return 42

@pytest.fixture
def assist():
    app = Flask(__name__)
    module = AppModule()
    injector = Injector([module])
    assist = Assistant(app, project_id="test-project-id", injector=injector)

    @assist.action("simple_intent")
    def simple_intent():
        speech = "Yes"
        return ask(speech)

    @inject
    @assist.action("simple_intent_with_inject")
    def simple_intent_with_inject(speech: str):
        return ask(speech)

    @inject
    @assist.action("simple_intent_with_inject_and_param")
    def simple_intent_with_inject_and_param(speech: str, param):
        return ask(param + "." + speech)

    @inject
    @assist.action("intent_with_injects_and_2_param")
    def intent_with_injects_and_2_param(speech: str, p1, p2, i: int):
        return ask(speech + ":" + p1 + ":" + p2 + ":" +str(i))

    @assist.action("add_context_1")
    def add_context():
        speech = "Adding context to context_out"
        manager.add("context_1")
        return ask(speech)

    @assist.context("context_1")
    @assist.action("intent_with_context_injects_params")
    @inject
    def intent_with_context_injects_params(speech: str, p1, p2, i: int):
        return ask("context_1:" +speech + ":" + p1 + ":" + p2 + ":" +str(i))

    return assist

def test_simple_intent(assist):
    client = assist.app.test_client()
    payload = build_payload("simple_intent")
    resp = get_query_response(client, payload)
    assert "Yes" in resp["fulfillmentText"]

def test_simple_intent_with_injection(assist):
    client = assist.app.test_client()
    payload = build_payload("simple_intent_with_inject")
    resp = get_query_response(client, payload)
    assert "TEST INJECTED" in resp["fulfillmentText"]

def test_simple_intent_with_inject_and_param(assist):
    client = assist.app.test_client()
    payload = build_payload("simple_intent_with_inject_and_param",params={"param": "blue"})
    resp = get_query_response(client, payload)
    assert "blue.TEST INJECTED" in resp["fulfillmentText"]

def test_intent_with_injects_and_2_params(assist):
    client = assist.app.test_client()
    payload = build_payload("intent_with_injects_and_2_param",params={"p1": "blue", "p2": "female"})
    resp = get_query_response(client, payload)
    assert "TEST INJECTED:blue:female:42" in resp["fulfillmentText"]

def test_intent_with_context_injects_and_params(assist):
    client = assist.app.test_client()
    payload = build_payload("add_context_1")
    resp = get_query_response(client, payload)
    payload = build_payload("intent_with_context_injects_params", contexts=resp["outputContexts"], params={"p1": "blue", "p2": "female"})
    resp = get_query_response(client, payload)
    assert "context_1:TEST INJECTED:blue:female:42" in resp["fulfillmentText"]



