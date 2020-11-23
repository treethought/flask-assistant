import dialogflow_v2beta1 as df
from google.protobuf.json_format import MessageToDict


def _build_info_response(
    text, title, img_url=None, img_alt=None, subtitle=None, link=None, link_title=None,
):

    info_resp = {"type": "info", "title": title, "subtitle": subtitle}

    if img_url:
        info_resp["image"] = {"src": {"rawlUrl": img_url}}

    if link:
        info_resp["actionLink"] = link

    return info_resp


def _build_description_response(text, title):

    descr_resp = {"type": "description", "title": title, "text": [text]}

    return descr_resp


def _build_button(link, link_title):
    btn = {
        "type": "button",
        "icon": {"type": "chevron_right", "color": "#FF9800"},
        "text": link_title,
        "link": link,
    }
    return btn
