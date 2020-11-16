import dialogflow_v2beta1 as df
from google.protobuf.json_format import MessageToDict


def build_card(
    text, title, img_url=None, img_alt=None, subtitle=None, link=None, link_title=None,
):

    button = df.types.intent_pb2.Intent.Message.Card.Button(
        text=link_title, postback=link
    )
    card = df.types.intent_pb2.Intent.Message.Card(title=title, subtitle=text)
    card.buttons.append(button)
    payload = MessageToDict(card)
    return {"card": payload, "lang": "en"}
    # card_payload = {"card": {"title": title, "subtitle": text, "formattedText": text}}
    # return card_payload
