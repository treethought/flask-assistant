import dialogflow_v2beta1 as df
from google.protobuf.json_format import MessageToDict


def build_card(
    text, title, img_url=None, img_alt=None, subtitle=None, link=None, link_title=None,
):

    info_resp = {"type": "info", "title": title, "subtitle": subtitle}

    if img_url:
        info_resp["image"] = {"src": {"rawlUrl": img_url}}

    if link:
        info_resp["actionLink"] = link

    return info_resp
