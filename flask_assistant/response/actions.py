def build_card(
    text,
    title,
    img_url=None,
    img_alt=None,
    subtitle=None,
    link=None,
    link_title=None,
    buttons=None,
):

    card_payload = {"title": title, "subtitle": subtitle, "formattedText": text}

    if buttons:
        card_payload["buttons"] = buttons

    elif link and link_title:
        btn_payload = [{"title": link_title, "openUriAction": {"uri": link}}]
        card_payload["buttons"] = btn_payload

    if img_url:
        img_payload = {"imageUri": img_url, "accessibilityText": img_alt or img_url}
        card_payload["image"] = img_payload

    return {"platform": "ACTIONS_ON_GOOGLE", "basicCard": card_payload}
