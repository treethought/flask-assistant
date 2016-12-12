    POST https:
        //my - service.com / action

    Headers:
    //user defined headers
    Content - type:
        application / json

    POST body:

    {
        "originalRequest": {
            "data": {
                "text": "shipping costs for asia",
                "match": [
                    "shipping costs for asia"
                ],
                "type": "message",
                "event": "direct_message",
                "team": "T0FJ03RMP",
                "user": "U0FLW1N95",
                "channel": "D4VTEALFP",
                "ts": "1478131884.000006"
            },
            "source": "slack_testbot"
        },
        "timestamp": "2016-11-03T00:11:24.706Z",
        "result": {
            "speech": "",
            "fulfillment": {
                "speech": "Shipping cost varies for the location the item needs to be shipped to. We will show you the cost, when you form the order in your cart.",
                "messages": [
                    {
                        "speech": "Shipping cost varies for the location the item needs to be shipped to. We will show you the cost, when you form the order in your cart.",
                        "type": 0
                    }
                ]
            },
            "score": 1.0,
            "source": "agent",
            "action": "shipping.cost",
            "resolvedQuery": "shipping costs for asia",
            "actionIncomplete": false,
            "contexts": [
                {
                    "name": "generic",
                    "parameters": {
                        "slack_channel": "D2VTEALFP",
                        "shipping-zone.original": "Asia",
                        "shipping-zone": "Asia",
                        "slack_user_id": "U0FLW1N93"
                    },
                    "lifespan": 4
                }
            ],
            "parameters": {
                "shipping-zone": "Asia"
            },
            "metadata": {
                "intentId": "e2eb1b9c-761d-4588-8b00-d7062128cb51",
                "webhookUsed": "true",
                "intentName": "shipping.cost"
            }
        },
        "sessionId": "fa08b2f0-a0f3-11e6-9a45-ef317d100c6e",
        "id": "cc8ca971-0eec-4a04-ab54-d2af01e4674e",
        "status": {
            "errorType": "success",
            "code": 200
        }
    }

    class _Request(object):
        """When an intent is triggered,
        API.AI sends data to the service in the form of POST request with
       a body in the format of response to a query.

       https://docs.api.ai/docs/webhook

       format -> https://docs.api.ai/docs/query#response
        """

        def __init__(self, api_request_payload):

            self.payload = api_request_payload
            





