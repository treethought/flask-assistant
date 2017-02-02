   
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