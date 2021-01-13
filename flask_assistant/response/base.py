from flask import json, make_response, current_app
from flask_assistant import logger
from flask_assistant.response import actions, dialogflow, hangouts, df_messenger


class _Response(object):
    """Base webhook response to be returned to Dialogflow"""

    def __init__(self, speech, display_text=None, is_ssml=False):

        self._speech = speech
        self._display_text = display_text
        self._integrations = current_app.config.get("INTEGRATIONS", [])
        self._messages = [{"text": {"text": [speech]}}]
        self._platform_messages = {}
        self._render_func = None
        self._is_ssml = is_ssml
        self._response = {
            "fulfillmentText": speech,
            "fulfillmentMessages": self._messages,
            "payload": {
                "google": {  # TODO: may be depreciated
                    "expect_user_response": True,
                    "is_ssml": True,
                    "permissions_request": None,
                }
            },
            "outputContexts": [],
            "source": "webhook",
            "followupEventInput": None,  # TODO
        }

        for i in self._integrations:
            self._platform_messages[i] = []

        if "ACTIONS_ON_GOOGLE" in self._integrations:
            self._set_user_storage()
            self._integrate_with_actions(self._speech, self._display_text, is_ssml)

    def add_msg(self, speech, display_text=None, is_ssml=False):
        self._messages.append({"text": {"text": [speech]}})

        if "ACTIONS_ON_GOOGLE" in self._integrations:
            self._integrate_with_actions(speech, display_text, is_ssml)

        return self

    def _set_user_storage(self):
        from flask_assistant.core import user

        # If empty or unspecified,
        # the existing persisted token will be unchanged.
        user_storage = user.get("userStorage")
        if user_storage is None:
            return

        if isinstance(user_storage, dict):
            user_storage = json.dumps(user_storage)

        if len(user_storage.encode("utf-8")) > 10000:
            raise ValueError("UserStorage must not exceed 10k bytes")

        self._response["payload"]["google"]["userStorage"] = user_storage

    def _integrate_with_df_messenger(self, speech=None, display_text=None):

        logger.debug("Integrating with dialogflow messenger")

        content = {"richContent": [[]]}
        for m in self._platform_messages.get("DIALOGFLOW_MESSENGER", []):
            content["richContent"][0].append(m)

        payload = {"payload": content}

        self._messages.append(payload)

    def _integrate_with_hangouts(self, speech=None, display_text=None, is_ssml=False):
        if display_text is None:
            display_text = speech

        self._messages.append(
            {"platform": "GOOGLE_HANGOUTS", "text": {"text": [display_text]},}
        )
        for m in self._platform_messages.get("GOOGLE_HANGOUTS", []):
            self._messages.append(m)

    def _integrate_with_actions(self, speech=None, display_text=None, is_ssml=False):
        if display_text is None:
            display_text = speech

        if is_ssml:
            ssml_speech = "<speak>" + speech + "</speak>"
            self._messages.append(
                {
                    "platform": "ACTIONS_ON_GOOGLE",
                    "simpleResponses": {
                        "simpleResponses": [
                            {"ssml": ssml_speech, "displayText": display_text}
                        ]
                    },
                }
            )
        else:
            self._messages.append(
                {
                    "platform": "ACTIONS_ON_GOOGLE",
                    "simpleResponses": {
                        "simpleResponses": [
                            {"textToSpeech": speech, "displayText": display_text}
                        ]
                    },
                }
            )

    def _include_contexts(self):
        from flask_assistant import core

        for context in core.context_manager.active:
            self._response["outputContexts"].append(context.serialize)

    def render_response(self):
        self._include_contexts()
        if self._render_func:
            self._render_func()

        self._integrate_with_df_messenger()
        self._integrate_with_hangouts(self._speech, self._display_text)
        logger.debug(json.dumps(self._response, indent=2))
        resp = make_response(json.dumps(self._response))
        resp.headers["Content-Type"] = "application/json"

        return resp

    def suggest(self, *replies):
        """Use suggestion chips to hint at responses to continue or pivot the conversation"""
        chips = []
        for r in replies:
            chips.append({"title": r})

        # native chips for GA
        self._messages.append(
            {"platform": "ACTIONS_ON_GOOGLE", "suggestions": {"suggestions": chips}}
        )

        if "DIALOGFLOW_MESSENGER" in self._integrations:
            existing_chips = False
            for m in self._platform_messages["DIALOGFLOW_MESSENGER"]:
                # already has chips, need to add to same object
                if m.get("type") == "chips":
                    existing_chips = True
                    break

            if not existing_chips:
                chip_resp = df_messenger._build_suggestions(*replies)
                self._platform_messages["DIALOGFLOW_MESSENGER"].append(chip_resp)

            else:
                df_chips = []
                for i in replies:
                    chip = df_messenger._build_chip(i)
                    df_chips.append(chip)

                for m in self._platform_messages["DIALOGFLOW_MESSENGER"]:
                    if m.get("type") == "chips":
                        m["options"].append(df_chips)

        return self

    def link_out(self, name, url):
        """Presents a chip similar to suggestion, but instead links to a url"""
        self._messages.append(
            {
                "platform": "ACTIONS_ON_GOOGLE",
                "linkOutSuggestion": {"destinationName": name, "uri": url},
            }
        )

        if "DIALOGFLOW_MESSENGER" in self._integrations:
            existing_chips = None
            for m in self._platform_messages["DIALOGFLOW_MESSENGER"]:
                # already has chips, need to add to same object
                if m.get("type") == "chips":
                    existing_chips = True
                    break

            link_chip = df_messenger._build_chip(name, url=url)

            if not existing_chips:
                chip_resp = {"type": "chips", "options": [link_chip]}
                self._platform_messages["DIALOGFLOW_MESSENGER"].append(chip_resp)

            else:
                for m in self._platform_messages["DIALOGFLOW_MESSENGER"]:
                    if m.get("type") == "chips":
                        m["options"].append(link_chip)

        return self

    def card(
        self,
        text,
        title,
        img_url=None,
        img_alt=None,
        subtitle=None,
        link=None,
        link_title=None,
        buttons=None,
        btn_icon=None,
        btn_icon_color=None,
    ):
        """Presents the user with a card response

        Cards may contain a title, body text, subtitle, an optional image,
        and a external link in the form of a button

        The only information required for a card are the text and title.

        example usage:

            resp = ask("Here's an example of a card")
            resp.card(
                text='The text to display',
                title='Card Title',
                img_url='http://example.com/image.png'
                link='https://google.com',
                link_title="Google it"
            )

            return resp


        Arguments:
            text {str} -- The boody text of the card
            title {str} -- The card title shown in header

        Keyword Arguments:
            img_url {str} -- URL of the image to represent the item (default: {None})
            img_alt {str} -- Accessibility text for the image
            subtitle {str} -- The subtitle displaye dbelow the title
            link {str} -- The https external URL to link to
            link_title {str} -- The text of the link button
            btn_icon {str} -- Icon from Material Icon library (DF_MESSENGER only) (default: chevron_right)
            btn_icon_color {str} -- Icon color hexcode (DF_MESSENGER only) (default: #FF9800)


        """
        df_card = dialogflow.build_card(
            text, title, img_url, img_alt, subtitle, link, link_title
        )
        self._messages.append(df_card)

        # df_messengar car is a combo of description + button
        if "DIALOGFLOW_MESSENGER" in self._integrations:

            description = df_messenger._build_description_response(text, title)
            self._platform_messages["DIALOGFLOW_MESSENGER"].append(description)

            if link:
                btn = df_messenger._build_button(
                    link, link_title, btn_icon, btn_icon_color
                )
                self._platform_messages["DIALOGFLOW_MESSENGER"].append(btn)

        if "GOOGLE_HANGOUTS" in self._integrations:
            hangouts_card = hangouts.build_card(
                text, title, img_url, img_alt, subtitle, link, link_title
            )
            self._platform_messages["GOOGLE_HANGOUTS"].append(hangouts_card)

        if "ACTIONS_ON_GOOGLE" in self._integrations:
            actions_card = actions.build_card(
                text, title, img_url, img_alt, subtitle, link, link_title, buttons
            )

            self._messages.append(actions_card)

        return self

    def build_list(self, title=None, items=None):
        """Presents the user with a vertical list of multiple items.

        Allows the user to select a single item.
        Selection generates a user query containing the title of the list item

        *Note* Returns a completely new object,
        and does not modify the existing response object
        Therefore, to add items, must be assigned to new variable
        or call the method directly after initializing list

        example usage:

            simple = ask('I speak this text')
            mylist = simple.build_list('List Title')
            mylist.add_item('Item1', 'key1')
            mylist.add_item('Item2', 'key2')

            return mylist

        Arguments:
            title {str} -- Title displayed at top of list card
            items {items} -- List of list items

        Returns:
            _ListSelector -- [_Response object exposing the add_item method]

        """

        list_card = _ListSelector(
            self._speech, display_text=self._display_text, title=title, items=items
        )
        return list_card

    def build_carousel(self, items=None):
        carousel = _CarouselCard(
            self._speech, display_text=self._display_text, items=items
        )
        return carousel

    def add_media(self, url, name, description=None, icon_url=None, icon_alt=None):
        """Adds a Media Card Response

        Media responses let your Actions play audio content with a
        playback duration longer than the 240-second limit of SSML.

        Can be included with ask and tell responses.
        If added to an `ask` response, suggestion chips

         Arguments:
            url {str} -- Required. Url where the media is stored
            name {str} -- Name of media card.

        Optional:
            description {str} -- A description of the item (default: {None})
            icon_url {str} -- Url of icon image
            icon_alt {str} -- Accessibility text for icon image

        example usage:

            resp = ask("Check out this tune")
            resp = resp.add_media(url, "Jazzy Tune")
            return resp_with_media.suggest("Next Song", "Done")


        """
        media_object = {"contentUrl": url, "name": name}
        if description:
            media_object["description"] = description

        if icon_url:
            media_object["largeImage"] = {}
            media_object["largeImage"]["imageUri"] = icon_url
            media_object["largeImage"]["accessibilityText"] = icon_alt or name

        self._messages.append(
            {
                "platform": "ACTIONS_ON_GOOGLE",
                "mediaContent": {"mediaObjects": [media_object], "mediaType": "AUDIO",},
            }
        )
        return self


def build_button(title, link):
    return {"title": title, "openUriAction": {"uri": link}}


def build_item(
    title,
    key=None,
    synonyms=None,
    description=None,
    img_url=None,
    alt_text=None,
    event=None,
):
    """
    Builds an item that may be added to List or Carousel

    "event" represents the Dialogflow event to be triggered on click for Dialogflow Messenger

    Arguments:
        title {str} -- Name of the item object

    Keyword Arguments:
        key {str} -- Key refering to the item.
                    This string will be used to send a query to your app if selected
        synonyms {list} -- Words and phrases the user may send to select the item
                            (default: {None})
        description {str} -- A description of the item (default: {None})
        img_url {str} -- URL of the image to represent the item (default: {None})
        event {dict} -- Dialogflow event to be triggered on click (DF_MESSENGER only)

    Example:

    item = build_item(
        "My item 1",
        key="my_item_1",
        synonyms=["number one"],
        description="The first item in the list",
        event={"name": "my-select-event", parameters={"item": "my_item_1"}, languageCode: "en-US"}
    )

    """
    item = {
        "info": {"key": key or title, "synonyms": synonyms or []},
        "title": title,
        "description": description,
        "event": event,
    }

    if img_url:
        img_payload = {
            "imageUri": img_url,
            "accessibilityText": alt_text or "{} img".format(title),
        }
        item["image"] = img_payload

    return item


class _CardWithItems(_Response):
    """Base class for Lists and Carousels to inherit from.

       Provides the meth:add_item method.
    """

    def __init__(self, speech, display_text=None, items=None):
        super(_CardWithItems, self).__init__(speech, display_text)
        self._items = items or list()
        self._render_func = self._add_message

    def _add_message(self):
        raise NotImplementedError

    def add_item(
        self, title, key, synonyms=None, description=None, img_url=None, event=None,
    ):
        """Adds item to a list or carousel card.

        A list must contain at least 2 items, each requiring a title and object key.

        Arguments:
            title {str} -- Name of the item object
            key {str} -- Key refering to the item.
                        This string will be used to send a query to your app if selected

        Keyword Arguments:
            synonyms {list} -- Words and phrases the user may send to select the item
                              (default: {None})
            description {str} -- A description of the item (default: {None})
            img_url {str} -- URL of the image to represent the item (default: {None})
            event {dict} -- Dialogflow event to be triggered on click (DF_MESSENGER only)

        """
        item = build_item(title, key, synonyms, description, img_url, event=event)
        self._items.append(item)
        return self

    def include_items(self, *item_objects):
        if not isinstance(item_objects, list):
            item_objects = list(item_objects)
        self._items.extend(item_objects)

        return self


class _ListSelector(_CardWithItems):
    """Subclass of basic _Response to provide an instance capable of adding items."""

    def __init__(self, speech, display_text=None, title=None, items=None):
        self._title = title

        super(_ListSelector, self).__init__(speech, display_text, items)

    def _add_message(self):

        self._messages.append(
            {
                "platform": "ACTIONS_ON_GOOGLE",
                "listSelect": {"title": self._title, "items": self._items},
            }
        )
        self._add_platform_msgs()

    def _add_platform_msgs(self):

        if "DIALOGFLOW_MESSENGER" in self._integrations:
            list_resp = df_messenger._build_list(self._title, self._items)
            self._platform_messages["DIALOGFLOW_MESSENGER"].extend(list_resp)


class _CarouselCard(_ListSelector):
    """Subclass of _CardWithItems used to build Carousel cards."""

    def __init__(self, speech, display_text=None, items=None):
        super(_CarouselCard, self).__init__(speech, display_text, items=items)

    def _add_message(self):
        self._messages.append(
            {"platform": "ACTIONS_ON_GOOGLE", "carouselSelect": {"items": self._items}}
        )


class tell(_Response):
    def __init__(self, speech, display_text=None, is_ssml=False):
        super(tell, self).__init__(speech, display_text, is_ssml)
        self._response["payload"]["google"]["expect_user_response"] = False


class ask(_Response):
    def __init__(self, speech, display_text=None, is_ssml=False):
        """Returns a response to the user and keeps the current session alive.
        Expects a response from the user.

        Arguments:
            speech {str} --  Text to be pronounced to the user / shown on the screen
        """
        super(ask, self).__init__(speech, display_text, is_ssml)
        self._response["payload"]["google"]["expect_user_response"] = True

    def reprompt(self, prompt):
        repromtKey = "text_to_speech"
        if self._is_ssml:
            repromtKey = "ssml"
        repromtResponse = {}
        repromtResponse[repromtKey] = prompt
        self._response["payload"]["google"]["no_input_prompts"] = [repromtResponse]
        return self


class event(_Response):
    """Triggers an event to invoke it's respective intent.

    When an event is triggered, speech, displayText and services' data will be ignored.
    """

    def __init__(self, event_name, **kwargs):
        super(event, self).__init__(speech="")

        self._response["followupEventInput"] = {
            "name": event_name,
            "parameters": kwargs,
        }


class permission(_Response):
    """Returns a permission request to the user.

    Arguments:
        permissions {list} -- list of permissions to request for eg. ['DEVICE_PRECISE_LOCATION']
        context {str} -- Text explaining the reason/value for the requested permission
        update_intent {str} -- name of the intent that the user wants to get updates from
    """

    def __init__(self, permissions, context=None, update_intent=None):
        super(permission, self).__init__(speech=None)
        self._messages[:] = []

        if isinstance(permissions, str):
            permissions = [permissions]

        if "UPDATE" in permissions and update_intent is None:
            raise ValueError("update_intent is required to ask for UPDATE permission")

        self._response["payload"]["google"]["systemIntent"] = {
            "intent": "actions.intent.PERMISSION",
            "data": {
                "@type": "type.googleapis.com/google.actions.v2.PermissionValueSpec",
                "optContext": context,
                "permissions": permissions,
                "updatePermissionValueSpec": {"intent": update_intent},
            },
        }


class sign_in(_Response):
    """Initiates the  authentication flow for Account Linking

    After the user authorizes the action to access their profile, a Google ID token
    will be received and validated by the flask-assistant and expose user profile information
    with the `user.profile` local

    In order to complete the sign in process, you will need to create an intent with
    the `actions_intent_SIGN_IN` event
    """

    # Payload according to https://developers.google.com/assistant/conversational/helpers#account_sign-in
    def __init__(self, reason=None):
        super(sign_in, self).__init__(speech=None)

        self._messages[:] = []
        self._response = {
            "payload": {
                "google": {
                    "expectUserResponse": True,
                    "systemIntent": {
                        "intent": "actions.intent.SIGN_IN",
                        "data": {
                            "@type": "type.googleapis.com/google.actions.v2.SignInValueSpec"
                        },
                    },
                }
            }
        }
