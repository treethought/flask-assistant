from google.cloud import dialogflow_v2 as df
from google.protobuf.json_format import MessageToDict


def build_card(
    text, title, img_url=None, img_alt=None, subtitle=None, link=None, link_title=None,
):

    button = df.Intent.Message.Card.Button(
        text=link_title, postback=link
    )
    card = df.Intent.Message.Card(title=title, subtitle=text)
    card.buttons.append(button)
    payload = df.Intent.Message.Card.to_dict(card)
    return {"card": payload, "lang": "en"}
    # card_payload = {"card": {"title": title, "subtitle": text, "formattedText": text}}
    # return card_payload
