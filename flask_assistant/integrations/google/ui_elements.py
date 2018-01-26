
class BasicCard(object):
    """docstring for BasicCard"""

    def __init__(self, title=None, subtitle=None, body_text=None, img=None, btns=None, img_options=None):
        """Represents a BasicCard UI element object to be included in a RichResponse

        [description]

        Keyword Arguments:
            title {str} -- Overall title of the card. Optional.  (default: {None})
            subtitle {str} -- Card Subtitle (default: {None})
            body_text {str} -- Body text of the card. Supports a limited set of markdown syntax for formatting. Required, unless image is present.  (default: {None})
            img {Image} -- A hero image for the card. The height is fixed to 192dp. Optional. (default: {None})
            btns {Button} -- Currently at most 1 button is supported. Optional.  (default: {None})
            img_options {str} -- Type of image display option. Optional.  (default: {None})

        Raises:
            ValueError -- [description]
        """

        super(BasicCard, self).__init__()
        self.title = title
        self.subtitle = subtitle
        self.body_text = body_text
        self.img = img
        self.btns = btns
        self.img_options = img_options or 'DEFAULT'
        self._data = {}

        if self.img is None and self.body_text is None:
            raise ValueError('Body text or an image must be included in a card')

    def _load_data(self):
        self._data['title'] = self.title
        self._data['subtitle'] = self.subtitle
        self._data['formattedText'] = self.body_text
        self._data['image'] = self.img
        self._data['buttons'] = self.btns
        self._data['imageDisplayOptions'] = self.img_options

        return self._data


class Image(object):
    """docstring for Image"""

    def __init__(self, url, descr, height=None, width=None):
        super(Image, self).__init__()
        self.url = url
        self.descr = descr
        self.height = height
        self.width = width

    def _build(self):
        obj = {
            "url": self.url,
            "accessibilityText": self.descr,
            "height": self.width,
            "width": self.height,
        }
        return obj


class Button(object):
    """docstring for Button"""

    def __init__(self, title, url):
        super(Button, self).__init__()
        self.title = title
        self.url = url

    def _build(self):
        obj = {
            "title": self.title,
            "openUrlAction": {
                'url': self.url
            },
        }
        return obj


### OptionValueSpec Types ##

class SimpleOption(object):
    """docstring for SelectionItem"""

    def __init__(self, key, title, synonyms=None):
        super(SimpleOption, self).__init__()
        self.title. title
        self.key = key
        self.synonyms = synonyms

    def _load_data(self):
        self._data['optionInfo'] = {
            'key': self.key,
            'synonyms': self.synonyms
        }
        if self.title:
            self._data['title'] = self.title
        return self._data

    def add_synonym(self, syn):
        self._data['synonyms'].appened(syn)


class ListItem(object):
    """docstring for ListItem"""

    def __init__(self, title, synonyms=None, descr=None, image=None):
        super(ListItem, self).__init__()

        self.title = title
        self.synonyms = synonyms
        self.descr = descr
        self.image = image
        self._data = {}

        # docs for title and key both state they are sent to user
        # so use the same value until usage is clear
        self.option_info = {
            'key': self.title,
            'synonyms': self.synonyms
        }

    def _load_data(self):
        self._data['optionInfo'] = self.option_info
        self._data['title'] = self.title
        self._data['description'] = self.descr
        self._data['image'] = self.image
        return self._data


class ListSelect(object):
    """docstring for ListSelect"""

    def __init__(self, title=None, list_items=None):
        super(ListSelect, self).__init__()
        self.title = title
        self.list_items = list_items or []
        self._data = {}

    def attach_item(self, list_item):
        item_data = list_item._load_data()
        self.list_items.append(item_data)

    def add_item(self, title, synonyms=None, descr=None, image=None):
        item = ListItem(title, synonyms, descr, image)
        self.attach_item(item)

    def _load_data(self):
        return {
            'listSelect': {
                'title': self.title,
                'items': self.list_items
            }
        }
