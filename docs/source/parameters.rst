
 
   
********************
Accepting Parameters
********************
Action functions can accept parameters, which will be parsed from the API.AI request as `entities <https://docs.api.ai/docs/concept-entities#overview>`_

For a parameter value to be parsed by API.AI's NLP, it needs to relate to a defined entity.
In other words, the name of the parameter must be the name of the entity it relates to.

Entities are defined:
    - using YAML templates and the :doc:`schema <generate_schema>` command
    - within the API.AI console
    - as existing API.AI `System Entities <https://docs.api.ai/docs/concept-entities#section-system-entities>`_

Each entity is composed of entries, which represent a mapping between a reference value and a group of synonyms. Entities will be the specific value passed to the action function.


Parameters for Custom Entities
===============================

Given an entity ``color`` defined with the following template:

.. code-block:: yaml

    color:
      - blue      
      - red
      - green
        
An action function may accept a parameter referring to an `entry` (blue, red, green) of the ``color`` `entity`:

.. code-block:: python

    @assist.action('give-color')
    def echo_color(color):
        speech = "Your favorite color is {}".format(color)
        return tell(speech)


Mapping Parameters to API.AI System Entities
==============================================

Every parameter passed to an action function needs to correspond to a defined entity.
These ``entities`` require defined ``entries`` in order to be parsed using NLP.

With the `color` example above, we defined three entries (blue, red, and green). To allow our assistant to accurately parse and handle all the possible colors a user might say, we would need to provide a great number of entries.

Instead of defining many entries for common entity concepts (color, names, addresses, etc), you can utilize API.AI's `System Entities <https://docs.api.ai/docs/concept-entities#section-system-entities>`_.

To use system entities, simply provide a mapping of the parameter name to corresponding system entity:

.. code-block:: python

    @assist.action('give-color', mapping={'color': 'sys.color'})
    def echo_color(color):
        speech = "Your favorite color is {}".format(color)
        return tell(speech)

And in the user_says template:

.. code-block:: yaml

    give-color:

      UserSays:
        - My color is blue
        - I like red
          
      Annotations:
        - blue: sys.color

No entity-template is needed for the `sys.color` entity, as it is already defined. API.AI will automatically recognize any color spoken by the user to be parsed as its ``sys.color`` entity, and flask-assistant will match the correct parameter value to the `color` parameter.




Prompting for Parameters
========================

When an action function accepts a parameter, it is required unless a default is provided.

If the parameter is not provided by the user, or was not defined in a previous context, the action function will not be called.

This is where :meth:`prompt_for` comes in handy.

The :meth:`prompt_for <flask_assistant.assistant.prompt_for>` decorator is passed a parameter name and intent name, and is called if the intent's action function's parameters have not been supplied.

.. code-block:: python

    @assist.prompt_for('color', intent='give-color')
    def prompt_color(color):
        speech = "Sorry I didn't catch that. What color did you say?"
        return ask(speech)