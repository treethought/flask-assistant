from google.cloud import dialogflow_v2 as df
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

    button = df.Intent.Message.Card.Button(
        text=link_title, postback=link
    )
    card = df.Intent.Message.Card(title=title, subtitle=text)
    card.buttons.append(button)

    payload = df.Intent.Message.Card.to_dict(card)
    return {"card": payload, "platform": "GOOGLE_HANGOUTS", "lang": "en"}
