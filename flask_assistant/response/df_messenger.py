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


def _build_list(title, items):
    list_responses = []
    for i in items:
        item = {
            "type": "list",
            "title": i["title"],
            "subtitle": i["description"],
            "event": {"name": "", "languageCode": "", "parameters": {}},
        }
        list_responses.append(item)

    return list_responses


def _build_suggestions(*replies):
    chips = {"type": "chips", "options": []}
    for i in replies:
        chips["options"].append({"text": i})

    return chips
