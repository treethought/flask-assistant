************************
Generating Dialogflow Schema
************************

.. IMPORTANT:: Schema Generation with Flask-Assistant is not yet implemented for V2 of Dialogflow. Please define intents and entities in the Dialogflow console directly.

Flask-Assistant provides a command line utilty to automatically generate your agent's JSON schema and register the required information to communicate with Dialogflow.

This allows you to focus on building your entire webhook from your text editor while needing to interact with the Dialogflow web interface only for testing.


The ``schema`` command generates JSON objects representing Intents and Entities


Intent Schema
=============

When the ``schema`` command is run, Intent objects are created from each of your webhook's action decorated functions.


The following information is extracted from your webhook and is included in each intent object:

    - Intent name - from the :any:`@action` decorator
    - Action name - the name of the wrapped action function
    - Accepted parameters - action function's accepted parameters including their default values and if they are required

User Says Template
------------------

Additionally, a `User Says <https://docs.api.ai/docs/concept-intents#user-says>`_ template skeleton for each intent is created.
The template will be located within the newly created `templates` directory.

This template is written in YAML, and each intent is represented by the following structure:

.. code-block:: yaml


    intent-name:
      UserSays:
      -
      -
      Annotations:
      -
      -

Using the template, you can include:
    - `Examples <https://docs.api.ai/docs/concept-intents#user-says>`_ of phrases a user might say to trigger the intent
    - Annotations as a mapping of paramater values to entity types.

To provide examples phrases, simply write a phrase using natural language

.. code-block:: yaml

    order-pizza-intent:

      UserSays:
       - I want a small cheese pizza
       - large pepporoni pizza for delivery

You can then annotate parameter values within the phrase to their respective entity

.. code-block:: language

     order-pizza-intent:

      UserSays:
        - I want a small cheese pizza
        - large pepperoni pizza for delivery

      Annotations:
        - small: pizza-size
        - cheese: topping
        - pepperoni: topping
        - delivery: order-method

If the intent requires no parameters or you'd like Dialogflow to automaticcaly annotate the phrase, simply exclude the ``Annotations``  or leave it blank.

Re-running the ``schema`` command will then update your agent's Intents with the new user phrases, including their annotations.



Entity Schema
=============

The schema command also allows you to define custom `entities <https://docs.api.ai/docs/concept-entities>`_ which represent
concepts and serve as a powerful tool for extracting parameter values from natural language inputs.

In addition to the User Says template, an entities template is generated in the same `templates` directory.

Entity Template
---------------

The basic skeleton will include only the names of your agent's entities, which are taken from action function parameters.

Using the entities template, you can include:
    - The entity name
    - A list of entries, which represent a mapping between a reference value and a group of synonyms.

The basic structure of an entity within the template looks like this:

.. code-block:: yaml

    toppings:
      -
      -

You can provide entries by listing them under the entity name.

.. code-block:: yaml

    toppings:
      - cheese
      - ham
      - veggies
      - pepperoni

Synonyms can be added for each entry to improve Dialogflow's detection of the entity.

.. code-block:: yaml

    toppings:
      - cheese: ['plain']
      - ham : ['canadian bacon']
      - veggies: ['vegetarian', 'vegetables']
      - pepperoni









.. note:: Any pre-built Dialogflow `system entities <https://docs.api.ai/docs/concept-entities#section-system-entities>`_ (sys.color) will not be included in the template, as they are already defined within Dialogflow.





Running the command
==========================

This will require an existing Dialogflow agent, and your webhook should be within its own directory, as the utility will create two new folders in the app's root.

1. First obtain your agent's Developer access token from the `Dialogflow Console`_
2. Ensure you are in the same directory as your assistant and store your token as an environment variable
    .. code-block:: bash

        export DEV_ACCES_TOKEN='YOUR ACCESS TOKEN'
3. Run the `schema` command
    .. code-block:: bash

        schema my_assistant.py

This will generate a JSON object for each intent and entity used in your webhook as described above. The schema objects will be pushed to Dialogflow and create a new intent/entity or update the existing one if the object already exists.

You will see an output of status messages indicating if the registration was successful for each object.

You can view the JSON generated in the newly created `schema` directory.



.. _`Dialogflow Console`: https://console.dialogflow.com/api-client
