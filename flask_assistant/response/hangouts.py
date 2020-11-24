import dialogflow_v2beta1 as df
from google.protobuf.json_format import MessageToDict
import logging


def build_card(
    text, title, img_url=None, img_alt=None, subtitle=None, link=None, link_title=None,
):
    if link is None:
        logging.warning(
            "Hangouts Chat card will not render properly without a button link"
        )
        link = link_title

    if link_title is None:
        link_title = "Learn More"

    button = df.types.intent_pb2.Intent.Message.Card.Button(
        text=link_title, postback=link
    )
    card = df.types.intent_pb2.Intent.Message.Card(title=title, subtitle=text)
    card.buttons.append(button)

    payload = MessageToDict(card)
    return {"card": payload, "platform": "GOOGLE_HANGOUTS", "lang": "en"}
