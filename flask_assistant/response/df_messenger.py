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


def _build_button(link, link_title, icon=None, icon_color=None):
    btn = {
        "type": "button",
        "text": link_title,
        "link": link,
    }

    if icon is None:
        icon = "chevron_right"

    if icon_color is None:
        icon_color = "#FF9800"

    btn["icon"] = {"type": icon, "color": icon_color}

    return btn


def _build_list(title, items):
    list_responses = []
    empty_event = {"name": "", "languageCode": "", "parameters": {}}
    for i in items:

        item = {
            "type": "list",
            "title": i["title"],
            "subtitle": i["description"],
            "event": i.get("event", empty_event),
        }
        list_responses.append(item)

    return list_responses


def _build_chip(text, img=None, url=None):
    c = {"text": text}
    if img:
        c["image"] = {"src": {"rawUrl": img}}

    if url:
        c["link"] = url

    return c


def _build_suggestions(*replies):
    chips = {"type": "chips", "options": []}
    for i in replies:
        c = _build_chip(i)
        chips["options"].append(c)

    return chips
