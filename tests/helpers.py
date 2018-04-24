import json

def build_payload(intent, params={}, contexts=[], action='test_action', query='test query'):

    return json.dumps({
        "originalRequest": {
            "source": "google",
            "version": "2",
            "data": {
                "isInSandbox": False,
                "surface": {
                    "capabilities": [
                        {
                            "name": "actions.capability.AUDIO_OUTPUT"
                        },
                        {
                            "name": "actions.capability.SCREEN_OUTPUT"
                        },
                        {
                            "name": "actions.capability.MEDIA_RESPONSE_AUDIO"
                        },
                        {
                            "name": "actions.capability.WEB_BROWSER"
                        }
                    ]
                },
                "inputs": [
                    {}
                ],
                "user": {
                    "lastSeen": "2018-04-23T15:10:43Z",
                    "locale": "en-US",
                    "userId": "abcdefg",
                    "accessToken": "foobar"
                },
                "conversation": {
                    "conversationId": "123456789",
                    "type": "ACTIVE",
                    "conversationToken": "[]"
                },
                "availableSurfaces": [
                    {
                        "capabilities": [
                            {
                                "name": "actions.capability.AUDIO_OUTPUT"
                            },
                            {
                                "name": "actions.capability.SCREEN_OUTPUT"
                            }
                        ]
                    }
                ]
            }
        },
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



def get_query_response(client, payload):
    resp = client.post('/', data=payload)
    assert resp.status_code == 200
    return json.loads(resp.data.decode('utf-8'))
