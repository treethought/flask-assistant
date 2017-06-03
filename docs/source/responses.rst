*******************
Rendering Responses
*******************

Conversations are primarily driven by an Assistant's response to the user. Responses not only present the user with the outcome with of the tiggered action, but also control the dialogue by instigating the user to provide intents in a logical manner.

Flask-Assisant provides three primary response types as well as platform-specific rich message types.


Primary Types
=============

The primary responses include :any:`ask`, :any:`tell`, and :any:`event`. All rich messages extend the `ask` and `tell` constructs.

To import the repsonse types:

.. code-block:: python

    from flask_assistant import ask, tell, event, build_item


ask
---

To ask a question which expects a response from the user:

.. code-block:: python

    @assist.action('Kickit')
    def kick_it():
        return ask('Can I kick it?')


tell
----

To return a text/speech response to the user and end the session:

.. code-block:: python

    @assist.action('Answer')
    def answer():
        return tell('Yes you can!')

event
-----

To invoke another intent directly and bypass an exchange with the user, an :any:`event` can be triggered.

Assuming the intent "GoOnThen" contains an event named "first_verse", triggering the "Begin" intent will provide the user with the question "'Before this, did you really know what life was?"


.. code-block:: python


    @assist.action('GoOnThen')
    def first_verse():
        return ask('Before this, did you really know what life was?')

    @assist.action('Begin')
    def start_verse():
        return event('first_verse')

.. note:: The name of an intent's action function does not necessarily need to share the name of the intent's event, though it may often make sense and provide a cleaner representation of dialogue structure.

        Currently, `Events`_ must be defined within an Intent in the API.AI console.
        But support for event definitions is coming soon

Rich Messages
=============

In addidtion to the primary text/speech responses, Flask-Assistant plans to provide `Rich Messages`_ for various platforms.

Currently, Rich Messages are only support for Actions on Google.

Rich Messages for Actions on Google
====================================

By utlizing the following rich responses, an Assistant can easily integreate with Actions on Google and provide a greater experience on devices that support Google Assistant (Google Home and mobile phones).

To enable Actions on Google Integration:

.. code-block:: python

    app.config['ASSIST_ACTIONS_ON_GOOGLE'] = True

Displaying a Card
-----------------

Use a `Card`_  to present the user with summaries or concise information, and to allow users to learn more if you choose (using a weblink).

    - Image
    - Title
    - Sub-title
    - Text body
    - Link

The only information required for a card is the `text` paramter which is used to fill the text body.
    
    .. code-block:: python
    
                
        @assist.action('ShowCard')
        def show_card():

            resp = ask("Here's an example of a card")

            resp.card(text='The text to display'
                      title='Card Title',
                      img_url='http://example.com/image.png'
                      )

            return resp


Suggesting Other Intents
------------------------

Provide the user with a `Suggestion Chip`_ to hint at responses to continue or pivot the conversation.
The suggestion text is sent as a query to API.AI when selected and therefore should match a *User Says* phrase for the intent to be triggered.

So given the following intents:

.. code-block:: yaml

        HelpIntent:
          UserSays:
          - Get Help
          - help
        
        Restart:
          Usersays:
          - start over
        
        GetArtistInfo:
          Usersays:
          - radiohead
          - violent femmes
          - the books

          Annotations:
          - radiohead: artist
          - 'the books': artist
          

        


Provide suggestions for likely intents:

.. code-block:: python

    @assist.action('SuggestThings')
    def suggest_things():
        return ask('What's up?').suggest('help', 'start over', 'radiohead')



Linking to External Resources
-----------------------------

In addition to suggestion chips for guiding dialogue, `link_out` chips can be used to send the user to external URLS.

    .. code-block:: python
    
        @assist.action('ShowResources')
        def link_resources():
            resp = ask('Need some external help?')

            resp.link_out('Github Repo', 'https://github.com/treethought/flask-assistant')
            resp.link_out('Read The Docs', 'http://flask-assistant.readthedocs.io/en/latest/')


List Selectors
-----------------------
Lists present the user with a vertical list of multiple items and allows the user to select a single one.
Selecting an item from the list generates a user query (chat bubble) containing the title of the list item. This user query will be used to match an agent's intent just like any other query.

.. note:: There seems to be a discrepency bewteen API.AI and Actions on Google in regards to the selection of list items.
          Within the API.AI console, the items `key` is sent as the user query. However, Actions on Google sends the item's title.

          For proper results within both platforms, simply provide both the item's key and title as `User Says` phrase until the issue is resolved.


First, create primary response

.. code-block:: python

    @assist.action('ShowList')
    def action_func():

        # Basic speech/text response
        resp = ask("Here is an example list")

Then create a list with a title and assign to variable

.. code-block:: python

    # Create a list with a title and assign to variable
    mylist = resp.build_list("Awesome List")


Add items directly to list

.. code-block:: python

    mylist.add_item(title="Option 1", # title sent as query for Actions
                    key="option_1",  
                    img_url="http://example.com/image1.png",
                    description="Option 1's short description",
                    synonyms=['one', 'number one', 'first option'])

    mylist.add_item(title="Option 2",
                    key="option_2",  # key sent as query for API.AI
                    img_url="http://example.com/image2.png",
                    description="Option 2's short description",
                    synonyms=['two', 'number two', 'second option'])


Or build items independent of list and add them to the list later

.. code-block:: python

    new_item = build_item(title="Option 3",
                          key="option_3",  # key sent as query for API.AI
                          img_url="http://example.com/image3.png",
                          description="Option 3's short description",
                          synonyms=['three', 'number three', third option'])

    mylist.include_items(new_item)

    return mylist

.. WARNING:: Creating a list with `build_list` returns an instance of a new response class. Therfore the result is a serpeate object than the primary response used to call the `build_list` method. 

    The original primary response (*ask*/*tell*) object will not contain the list, and so the result should likely be assigned to a variable.


Carousels
---------

`Carousels`_ scroll horizontally and allows for selecting one item. They are very similar to list items, but provide richer content by providing multiple tiles resembling cards.

To build a carousel:

.. code-block:: python

    @assist.action('FlaskAssistantCarousel')
    def action_func():
        resp = ask("Here's a basic carousel").build_carousel()

        resp.add_item("Option 1 Title",
                      key="option_1",
                      description='Option 1's longer description,
                      img_url="http://example.com/image1.png")

        resp.add_item("Option 2 Title",
                      key="option_2",
                      description='Option 2's longer description,
                      img_url="http://example.com/image2.png")
        return resp





.. _`Events`: https://docs.api.ai/docs/concept-events#overview
.. _`Rich Messages`: https://docs.api.ai/docs/rich-messages
.. _`Card`: https://developers.google.com/actions/assistant/responses#basic_card
.. _`Suggestion Chip`: https://developers.google.com/actions/assistant/responses#suggestion-chip
.. _`Lists`: https://developers.google.com/actions/assistant/responses#list_selector
.. _`Carousels`: https://developers.google.com/actions/assistant/responses#carousel_selector



