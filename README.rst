
*************************************
Create Virtual Assistants with Python
*************************************

.. image:: https://badges.gitter.im/flask-assistant/Lobby.svg
   :alt: Join the chat at https://gitter.im/flask-assistant/Lobby
   :target: https://gitter.im/flask-assistant/Lobby?utm_source=badge&utm_medium=badge&utm_campaign=pr-badge&utm_content=badge


A flask extension serving as an `API.AI`_  SDK to provide an easy way to create virtual assistants which may be integrated with platforms such as `Actions on Google`_ (Google Assistant).

Flask-Assistant allows you to focus on building the core business logic of conversational user interfaces while utilizing API.AI's Natural Language Processing to interact with users.

**Recent Updates:**
   - Now providing `Rich Messages`_ for the Google Assistant!
   - Support for Flask Blueprints
   - Convenient `Home Assistant Integration`_


.. _`Actions on Google`: https://developers.google.com/actions/develop/apiai/ 
.. _`fullfillment`: https://developers.google.com/actions/develop/apiai/dialogs-and-fulfillment#overview
.. _API.AI: https://docs.api.ai/
.. _`Home Assistant`: https://home-assistant.io/
.. _`Home Assistant Integration`: http://flask-assistant.readthedocs.io/en/latest/hass.html
.. _`Rich Messages`: http://flask-assistant.readthedocs.io/en/latest/responses.html#rich-messages



.. **Anything you can code in python can be integrated into an assistant's capabilties!**

..     - Perfom complicated actions in response to simple user commands
..     - Integrate with platforms supported by API.AI (Actions on Google, Alexa, Slack, etc...)
..     - Interact with external services and APIs
..     - Retain information and respond to user requests in a context-specific manner
..     - Design conversational flow to build sophisticated contextual dialogues




This project is heavily inspired and based on John Wheeler's `Flask-ask <https://github.com/johnwheeler/flask-ask>`_ for the Alexa Skills Kit.


Features
========

    - Mapping of user-triggered Intents to action functions
    - Context support for crafting dialogue dependent on the user's requests
    - Define prompts for missing parameters when they are not present in the users request or past active contexts
    - A convenient syntax resembling Flask's decoratored routing
    - Internal API.AI schema generation and registration
    

Hello World
============

.. code-block:: python

    from flask import Flask
    from flask_assistant import Assistant, ask

    app = Flask(__name__)
    assist = Assistant(app)

    @assist.action('Demo')
    def hello_world():
        speech = 'Microphone check 1, 2 what is this?'
        return ask(speech)

    if __name__ == '__main__':
        app.run(debug=True)

How-To
=======

    1. Create an `Assistant` object with a Flask app and the route to your webhook URL.
    2. Use `action` decorators to map the intents to the proper action function.
    3. Use action view functions to return `ask` or `tell` responses.


Documentation
==============

- Check out the `Quick Start <http://flask-assistant.readthedocs.io/en/latest/quick_start.html>`_ to jump right in
- View the full `documentation <http://flask-assistant.readthedocs.io/en/latest/>`_


  



  









