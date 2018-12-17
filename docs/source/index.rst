.. Flask-Assistant documentation master file, created by
   sphinx-quickstart on Wed Jan 18 17:49:02 2017.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.


***************************
Welcome to Flask-Assistant!
***************************

.. _`Google Actions`: https://developers.google.com/actions/dialogflow/
.. _`fullfillment`: https://dialogflow.com/docs/fulfillment
.. _Dialogflow: https://dialogflow.com/docs

A flask extension serving as an `Dialogflow`_  SDK to provide an easy way to create virtual assistants which may be integrated with platforms such as `Google Actions`_ (Google Home).

Flask-Assistant allows you to focus on building the core business logic of conversational user interfaces while utilizing Dialogflow's Natural Language Processing to interact with users.


.. This framework provides the ability to:
.. ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
..     - Quickly create fullfillment_ webhooks
..     - Define and register Dialogflow schema
..     - Design a conversational flow to build contextual dialogues with Dialogflow's concept of contexts




Features
========

    - Maping of user-triggered Intents to action view functions
    - Context support for crafting dialogue dependent on the user's requests
    - Define prompts for missing parameters when they are not present in the users request or past active contexs
    - A convenient syntax resembling Flask's decoratored routing
    - Internal Dialogflow schema generation and registration



A Minimal Assistant
===================

.. code-block:: python

    from flask import Flask
    from flask_assistant import Assistant, tell

    app = Flask(__name__)
    assist = Assistant(app, project_id='GOOGLE_CLOUD_PROJECT_ID')

    @assist.action('Demo')
    def hello_world():
        speech = 'Microphone check 1, 2 what is this?'
        return tell(speech)

    if __name__ == '__main__':
        app.run(debug=True)

As you can see, structure of an Assistant app resembles the structure of a regular Flask app.

Explanation
-----------

1. Initialized an :class:`Assistant <flask_assistant.Assistant>` object with a Flask app and the route to your webhook URL.
2. Used the :meth:`action <flask_assistant.Assistant.action>` decorator to map the `greetings` intent to the proper action function.
    - The action decorator accepts the name of an intent as a parameter
    - The decorated function serves as the action view function, called when an Dialogflow request sent on behalf of the `send-message` intent is received
3. The action function returns an :class:`ask <flask_assistant.ask>` response containing text/speech which prompts the user for the next intent.


Check out the :doc:`quick_start` to see how to quickly build an assistant


.. include:: contents.rst.inc

.. Indices
.. ==================

.. * :ref:`genindex`
.. * :ref:`modindex`
.. * :ref:`search`
