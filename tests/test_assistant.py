from flask_assistant.manager import Context
from tests.helpers import build_payload, get_query_response



def test_intents_with_different_formatting(simple_client, intent_payload):

    resp = get_query_response(simple_client, intent_payload)
    assert 'Message' in resp['speech']

    resp = simple_client.post('/', data=intent_payload)
    assert resp.status_code == 200

    assert b'Message' in resp.data


def test_add_context_to_response(context_assist):
    client = context_assist.app.test_client()
    payload = build_payload('AddContext')
    resp = get_query_response(client, payload)
    context_item = {'lifespan': 5, 'name': 'SampleContext', 'parameters': {}}
    assert context_item in resp['contextOut']

def test_add_context_to_manager(context_assist):
    # with statement allows context locals to be accessed
    # remains within the actual request to the flask app 
    with context_assist.app.test_client() as client:
        payload = build_payload('AddContext')
        resp = get_query_response(client, payload)
        context_obj = Context('SampleContext')
        assert context_obj in context_assist.context_manager.active

# def test_need_context_to_match_action(context_assist):
#     with context_assist.app.test_client() as client:
#         payload = build_payload('ContextRequired')
#         resp = get_query_response(client, payload)
#         assert 'Matched because SampleContext was active' not in resp['speech']


def test_docs_context(docs_assist):

    # adds 'vegetarian' context
    with docs_assist.app.test_client() as client:
        payload = build_payload('give-diet', params={'diet': 'vegetarian'})
        resp = get_query_response(client, payload)
        context_obj = Context('vegetarian')
        assert context_obj in docs_assist.context_manager.active

        next_payload = build_payload('get-food', contexts=resp['contextOut'])
        next_resp = get_query_response(client, next_payload)
        assert 'farmers market' in next_resp['speech']

    # adds 'carnivore' context
    with docs_assist.app.test_client() as client:
        payload = build_payload('give-diet', params={'diet': 'carnivore'})
        resp = get_query_response(client, payload)
        context_obj = Context('carnivore')
        assert context_obj in docs_assist.context_manager.active

        next_payload = build_payload('get-food', contexts=resp['contextOut'])
        next_resp = get_query_response(client, next_payload)
        assert 'farmers market' not in next_resp['speech']
        assert 'BBQ' in next_resp['speech']




