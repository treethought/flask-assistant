***********
Quick Start
***********

This page will provide a walk through of making a basic assistant

Installation
============
.. code-block:: bash

    pip install flask-assistant

Setting Up the Project
======================

Create a directory to serve as the app root (useful if auto-generating Intent schema)

.. code-block:: bash

    mkdir my_assistant
    cd my_assistant

    touch webhook.py


Server Setup
------------
This example will use ``ngrok`` to quickly provide a public URL for the flask-assistant webhook. This is required for Dialogflow to communicate with the assistant app.

Make sure you have `ngrok`_ installed and start an http instance on port 5000.

- .. code-block:: bash

    ./ngrok http 5000

A status message similiar to the one below will be shown.

::

    ngrok by @inconshreveable                                                                                      (Ctrl+C to quit)

    Session Status                online
    Version                       2.1.18
    Region                        United States (us)
    Web Interface                 http://127.0.0.1:4040
    Forwarding                    http://1ba714e7.ngrok.io -> localhost:5000
    Forwarding                    https://1ba714e7.ngrok.io -> localhost:5000

Note the **Forwarding https** URL.
    - ``https://1ba714e7.ngrok.io`` in the above example.
    - This is the URL that will be used as the Webhook URL in the Dialogflow console as described below.


..  _api_setup:

Dialogflow Setup
------------

1. Sign in to the `Dialogflow Console`_
2. Create a new Agent_ named "HelloWorld" and click save.
3. Click on Fullfillment in the left side menu and enable webhook.
4. Provide the ``https`` URL from the `ngrok` status message as the webhook URL.

.. 5. Create a new project in the `Google Developer Console`_


.. Step 5 is not required for test your app within the Dialogflow console, but is if you plan to test or deploy on Google Home


.. note:: You can create new intents and provide information about their action and parameters
        in the web interface and they will still be matched to your assistant's action function for the intent's name.

        However, it may often be simpler to define your intents directly from your assistant as will be shown here.







Create your Webhook
====================

Create a directory to serve as the app root.

.. code-block:: bash

    mkdir my_assistant
    cd my_assistant

Create a a new file for your assistant's webhook

.. code-block:: bash

    touch webhook.py



In your new webhook.py file:


.. code-block:: python

    from flask import Flask
    from flask_assistant import Assistant, ask, tell

    app = Flask(__name__)
    assist = Assistant(app, route='/')


    @assist.action('greeting')
    def greet_and_start():
        speech = "Hey! Are you male or female?"
        return ask(speech)

    if __name__ == '__main__':
        app.run(debug=True)

Here, we have defined an action function to be called if the 'greeting' intent is matched.
The action function returns a response to Dialogflow which greets the user and asks the user for their gender.

Now let's define the action to be performed when the user provides their gender.


.. code-block:: python

    @assist.action("give-gender")
    def ask_for_color(gender):
        if gender == 'male':
            gender_msg = 'Sup bro!'
        else:
            gender_msg = 'Haay gurl!'

        speech = gender_msg + ' What is your favorite color?'
        return ask(speech)

When the user gives their gender as a response to the ``greet_and_start`` action, it matches the `give-gender` intent and triggers the ``ask_for_color`` action.

The gender value will be parsed as an `entity <https://dialogflow.com/docs/entities>`_ from the user's phrase, identified as a parameter and passed to the action function.

In order for the gender to be recognized by Dialogflow, we will need to :ref:`define and register <schema>` an entity with Dialogflow.


Before we define our entity, let's first finish the webhook by defining the final action, which will occur after the user provides their favorite color.

.. code-block:: python

    @assist.action('give-color', mapping={'color': 'sys.color'})
    def ask_for_season(color):
        speech = 'Ok, {} is an okay color I guess'.format(color)
        return ask(speech)


Because this action requires the ``color`` parameter, a color entity needs to be defined within our Dialogflow agent.
However, there are a very large number of colors that we'd like our Dialogflow to recognize as a color entity.

Instead of defining our own ``color`` entity and all of the possible entries for the entity (as we will do with ``gender``), we will utilize one of Dialogflow's `System Entities <https://dialogflow.com/docs/entities/system-entities>`_.

To do this we simply mapped the  ``color`` parameter to the `sys.color` System Entity:

.. code-block:: python

    @assist.action('give-color', mapping={'color': 'sys.color'})

.. This allows flask-assistant to grab the value of ``color`` from the

Now we do not need to provide any definition about the ``color`` entity, and Dialogflow will automaticlly recognize any color spoken by the user to be parsed as a ``sys.color`` entity.





.. _schema:

Registering Schema
===================================
At this point our assistant app has three intents: ``greeting`` and ``give-gender`` and ``give-color``.
They are defined with the :meth:`action <flask_assistant.Assistant.action>` decorator, but how does Dialogflow know that these intents exist and how does it know what the user should say to match them?

Flask-assistant includes a command line utilty to automatically create and register required schema with Dialogflow.

Let's walk through how to utilize the :doc:`schema <generate_schema>` command.





Run the schema command
----------------------

1. First obtain your agent's Access Tokens from the `Dialogflow Console`_.
2. Ensure you are in the same directory as your assistant and store your token as an environment variable
    .. code-block:: bash

        cd my_assistant
        export DEV_ACCESS_TOKEN='YOUR DEV TOKEN'
        export CLIENT_ACCESS_TOKEN='YOUR CLIENT TOKEN'

3. Run the `schema` command
    .. code-block:: bash

        schema webhook.py

The ``schema`` command will then output the result of registering intents and entities.

With regards to the intent registration:
::

    Generating intent schema...

    Registering greeting intent
    {'status': {'errorType': 'success', 'code': 200}, 'id': 'be697c8a-539d-4905-81f2-44032261f715'}

    Registering give-gender intent
    {'status': {'errorType': 'success', 'code': 200}, 'id': '9759acde-d5f4-4552-940c-884dbcd8c615'}

    Writing schema json to file

Navigate to your agent's Intents section within the `Dialogflow Console`_. You will now see that the ``greeting``, ``give-gender`` and ``give-color`` intents have been registered.

However, if you click on the ``give-gender`` intent, you'll see an error pop-up message that the `gender` entity hasn't been created. This is expected from the ``schema`` output message for the entities registration:

::
    Generating entity schema...

    Registering gender entity
    {'timestamp': '2017-02-01T06:09:03.489Z', 'id': '0d7e278d-84e3-4ba8-a617-69e9b240d3b4',
    'status': {'errorType': 'bad_request', 'code': 400, 'errorDetails': "Error adding entity. Error in entity 'gender'. Entry value is empty, this entry will be skipped. . ", 'errorID': '21f62e16-4e07-405b-a201-e68f8930a88d'}}

To fix this, we'll use the templates created from the schema command to provide more compelete schema.



Using the schema Templates
--------------------------

The schema command creates a new `templates/` directory containing two YAML template skeletons:

``user_says.yaml`` is used to:
    - Define phrases a user will say to match specific intents
    - Annotate parameters within the phrases as specific entity types

``entities.yaml`` is used to:
    - Define `entities`_
    - Provide entries (examples of the entity type) and their synonyms

Entity Template
^^^^^^^^^^^^^^^^

Let's edit `templates/entities.yaml` to provide the needed schema to register the gender entity.

Initially, the template will contain a simple declaration of the entity names, but will be missing the entities' entries.

.. code-block:: yaml

    gender:
     -
     -

Entries represent a mapping between a reference value and a group of synonyms. Let's add the appropriate entries for the gender entity.

.. code-block:: yaml

    gender:
     - male: ['man', 'boy', 'guy', 'dude']
     - female: ['woman', 'girl', 'gal']

.. note:: Any pre-built Dialogflow system entities (sys.color) will not be included in the template, as they are already defined within Dialogflow.

.. _user_says_templ:

User Says Template
^^^^^^^^^^^^^^^^^^

Now we will fill in the `templates/user_says.yaml` template to provide examples of what the user may say to trigger our defined intents.

After running the ``schema`` command, the User Says Template will include a section for each intent.


For example, the give-color intent will look like:

.. code-block:: yaml


    give-color:
      UserSays:
      -
      -
      Annotations:
      -
      -

To fill in the template, provide exmaples of what the user may say under ``UserSays`` and a mapping of paramater value to entity type under ``Annotations``.

.. code-block:: yaml

    give-color:

      UserSays:
      - my color is blue
      - Its blue
      - I like red
      - My favorite color is red
      - blue

      Annotations:
      - blue: sys.color
      - red: sys.color


    give-gender:

      UserSays:
      - male
      - Im a female
      - girl

      Annotations:
      - male: gender
      - female: gender
      - girl: gender

If the intent requires no parameters or you'd like Dialogflow to automatically annotate the phrase, simply exclude the ``Annotations``  or leave it blank.

.. code-block:: yaml

    greeting:
      UserSays:
      - hi
      - hello
      - start
      - begin
      - launch



Now that the templates are filled out, run the schema command again to update exsting Intents schema and register the newly defined `gender` entity.

    .. code-block:: bash

        schema webhook.py

Testing the Assistant
=====================

Now that the schema has been registered with Dialogflow, we can make sure everything is working.

Add the following to set up logging so that we can see the Dialogflow request and flask-assistant response JSON.

.. code-block:: python

    import logging
    logging.getLogger('flask_assistant').setLevel(logging.DEBUG)

.. code-block:: bash

    python webhook.py

You can now interact with your assistant using the `Try it now..` area on the right hand side of the `Dialogflow Console`_.



Integrate with Actions on Google
=================================

With the webhook logic complete and the Dialogflow agent set up, you can now easily
integrate with Actions on Google. This will allow you to preview and deploy your assistant on Google Home.

To integrate with Actions on Google, follow this simple `guide <https://dialogflow.com/docs/integrations/actions#overview>`_ from Dialogflow.

More info on how to integrate your assistant with various platforms can be found `here <https://dialogflow.com/docs/integrations>`_.




















.. _`entities`: https://dialogflow.com/docs/entities




















.. _

.. _`Dialogflow Console`: https://console.dialogflow.com
.. _`Agent`: https://console.dialogflow.com/api-client/#/newAgent
.. _`Google Developer Console`: https://console.developers.google.com/projectselector/apis/api/actions.googleapis.com/overview
.. _`Flask-Live-Starter`: https://github.com/johnwheeler/flask-live-starter
.. _`ngrok`: https://ngrok.com/
