from flask_assistant.response import _Response


class _ActionResponse(_Response):
    """docstring for _ActionResponse"""

    def __init__(self, speech):
        super(_ActionResponse, self).__init__(speech)
        self._response['messages'] = [{
            "type": "simple_response",
            "platform": "google",
            "textToSpeech": speech
        }]

    def with_speech(self, speech):
        self._response['messages'].append({
            "type": "simple_response",
            "platform": "google",
            "textToSpeech": speech
        })
        return self


class simple(_ActionResponse):
    """docstring for simple"""

    def __init__(self, speech):
        super(simple, self).__init__(speech)

        self._response['messages'] = [
            {
                "type": "simple_response",
                "platform": "google",
                "textToSpeech": speech
            }
        ]


class card(_ActionResponse):

    def __init__(self, speech, text, title=None, img_url=None, img_alt=None, subtitle=None, link=None):
        super(card, self).__init__(speech)
        self._response['messages'].append(
            {
                "type": "basic_card",
                "platform": "google",
                "title": title,
                "formattedText": text,
                "image": {'url': img_url, 'accessibilityText': img_alt},
                "buttons": []
            }
        )


class list_selector(_ActionResponse):

    def __init__(self, speech, title=None, items=[]):
        super(list_selector, self).__init__(speech)
        self._items = items
        self._response['messages'].append(
            {
                "type": "list_card",
                "platform": "google",
                "title": title,
                "items": self._items
            }
        )

    def add_item(self, title, key, synonyms=None, description=None, img_url=None):
        item = {
            'option_info': {
                'key': key,
                'synonyms': synonyms
            },
            'title': title,
            'description': description,
            'image': {'url': img_url}
        }
        self._items.append(item)
