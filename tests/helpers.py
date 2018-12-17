import json


def build_payload(
    intent, params={}, contexts=[], action="test_action", query="test query"
):

    return json.dumps(
        {
            "originalDetectIntentRequest": {
                "source": "google",
                "version": "2",
                "data": {
                    "isInSandbox": False,
                    "surface": {
                        "capabilities": [
                            {"name": "actions.capability.AUDIO_OUTPUT"},
                            {"name": "actions.capability.SCREEN_OUTPUT"},
                            {"name": "actions.capability.MEDIA_RESPONSE_AUDIO"},
                            {"name": "actions.capability.WEB_BROWSER"},
                        ]
                    },
                    "inputs": [{}],
                    "user": {
                        "lastSeen": "2018-04-23T15:10:43Z",
                        "locale": "en-US",
                        "userId": "abcdefg",
                        "accessToken": "foobar",
                    },
                    "conversation": {
                        "conversationId": "123456789",
                        "type": "ACTIVE",
                        "conversationToken": "[]",
                    },
                    "availableSurfaces": [
                        {
                            "capabilities": [
                                {"name": "actions.capability.AUDIO_OUTPUT"},
                                {"name": "actions.capability.SCREEN_OUTPUT"},
                            ]
                        }
                    ],
                },
            },
            "responseId": "8ea2d357-10c0-40d1-b1dc-e109cd714f67",
            "queryResult": {
                "action": action,
                "allRequiredParamsCollected": True,
                "outputContexts": contexts,
                "languageCode": "en",
                "fulfillment": {"messages": [], "text": ""},
                "intent": {
                    "name": "some-intent-id",
                    "displayName": intent,
                    # "webhookForSlotFillingUsed": "false",
                    "webhookState": True,
                },
                "parameters": params,
                "resolvedQuery": query,
                "intentDetectionConfidence": 1.0,
            },
            "session": "projects/test-project-id/agent/sessions/88d13aa8-2999-4f71-b233-39cbf3a824a0",
        }
    )


def get_query_response(client, payload):
    resp = client.post("/", data=payload)
    assert resp.status_code == 200
    return json.loads(resp.data.decode("utf-8"))
