***********
Quick Start
***********

This page will go over some of the key concepts of flask-assistant

Installation
============
.. code-block:: bash

    pip install flask-assistant


Create a directory to serve as the app root (useful if auto-generating Intent schema)

.. code-block:: bash

    mkdir my_assistant
    cd my_assistant



..  _api_setup:

API.AI Setup
============
1. Sign in to the `API.AI Console`_
2. Create a new Agent_ named "Hello World" and click save.
3. Click on Fullfillment in the left side menu and enable webhook
    - Provide the publically available URL to the flask app will receive requests at
    - This can be easily done using `ngrok`_
    - or `Flask-Live-Starter`_
4. Create a new project in the `Google Developer Console`_
   

Step 4 is not required for test your app within the API.AI console, but is if you plan to test or deploy on Google Home

   
.. note:: You can create new intents and provide information about their action and parameters
        in the web interface and they will still be matched to your assistant's action function for the intent's name.
        However, it may often be simpler to define your intents directly from your assistant as will be shown here.


Create your Assistant
=====================


.. code-block:: python

    from flask import Flask
    from flask_assistant import Assistant, tell

    app = Flask(__name__)
    assist = Assistant(app, '/')


    @assist.action('greetings')
    def greetings():
        speech = """Hello, what is your favorite color?"""
        return ask(speech)

    if __name__ = '__main__':
        app.run(debug=True)


As you can see, structure of an Assistant app resembles the structure of a regular Flask.

Explanation
-----------

1. Initialized an :class:`Assistant <flask_assistant.Assistant>` object with a Flask app and the route to your webhook URL.
2. Used the :meth:`action <flask_assistant.Assistant.action>` decorator to map the `greetings` intent to the proper action function.
    - The action decorator accepts the name of an intent as a parameter
    - The decorated function serves as the action view function, called when an API.AI request sent on behalf of the `send-message` intent is received
3. The action funtion returns an :class:`ask <flask_assistant.ask>` response containing text/speech which prompts the user for the next intent.


   
Accepting Parameters
====================
Action functions can accept parameters, which will be parsed from the API.AI request


.. code-block:: python

    @assist.action('give-color')
    def echo_color(color):
        speech = "Your favorite color is {}".format(color)
        return tell(speech)


Because the action view function requires a parameter, it will not be called if the color parameter
is not provided by the user, or if it was not defined previously in an active :doc:`context contexts`
This is where :meth:`prompt_for` comes in handy.



Prompting for Parameters
========================

The :meth:`prompt_for <flask_assistant.assistant.prompt_for>` decorator is passed a parameter name and intent name, and is called if the intent's action function's parameters have not been supplied.

.. code-block:: python

    @assist.prompt_for('color', intent='give-color')
    def prompt_color(color):
        speech = "Sorry I didn't catch that. What color did you say?"
        return ask(speech)
        












.. _

.. _`API.AI Console`: https://console.api.ai/api-client/#/login
.. _`Agent`: https://console.api.ai/api-client/#/newAgent
.. _`Google Developer Console`: https://console.developers.google.com/projectselector/apis/api/actions.googleapis.com/overview
.. _`Flask-Live-Starter`: https://github.com/johnwheeler/flask-live-starter
.. _`ngrok`: https://ngrok.com/

