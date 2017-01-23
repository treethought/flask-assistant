
**************
Using Context
**************

Overview
========

Flask-assitant supports API.AI's concept of `contexts <https://docs.api.ai/docs/concept-contexts>`_.

Contexts help to store and persist accessible information over multiple requests and define the "state" of the current session.
You can create different contexts based on the actions your assistant performs and use the generated contexts to determine which intents may be triggered (and thus which actions may take place) in future requests.

The use of contexts allows for a more dynamic dialogue and is helpful for differentiating phrases which may be vague or have different meanings depending on the user’s preferences or geographic location, the current page in an app, or the topic of conversation.

Intents may require input contexts, and their actions may set output contexts. 


Context Objects
===============

Input Contexts

    - Input contexts limit intents to be matched only when certain contexts are set.
    - They essentially act as requirements for a particular intent's action function to be called.
    - They are received in every request from API.AI under a "contexts" element, and consist of any previously declared output contexts
      
Output Contexts

    - Output contexts are set by actions to share information across requests within a session and are received as Input Contexts for future intents.
    - If an input context is modified within in action, the changes will persist via a new output context.
      
In a REST-like fashion, all declared contexts are received in every request from API.AI and included in every response from your assistant. Flask-assistant provides the :any:`context_manager` to automatically handle this exchange and preserve the state of the conversation.



.. Flask-assistant provides two mechanisms for utilizing contexts to build dialogues: the :any:`context_manager` and :meth:`@context <flask_assistant.core.context>`


Context Manager
==================================



The :any:`context_manager` is used to declare, access, and modify context objects. It contains the input contexts recieved from the  API.AI request and appends any new or modified contexts to the flask-assistant response.


.. It is available as a `LocalProxy <http://werkzeug.pocoo.org/docs/0.11/local/#werkzeug.local.LocalProxy>`_ and


.. code-block:: python

    from flask_assistant import context_manager


Add a new context:

.. code-block:: python

    context_manager.add('context-name')


Retrieve a declared context:

.. code-block:: python

    my_context = context_manager.get('context-name')


Set a parameter value directly on a context object...

.. code-block:: python

    my_context.set('foo', bar)

Or via the context_manager:

.. code-block:: python

    context_manager.set('context-name', 'param_name', value)


context decorator
==================

The :any:`context` decorator restricts a wrapped action function to be matched only if the given contexts are active.

While the :any:`context_manager` is used create and access context objects, the :any:`context` decorator is responsible for mapping an intent to one of possibly many context-dependent action functions.

The basic :any:`action` intent-mapping in conjuction with :any:`context` action filtering allows
a single intent to invoke an action appropriate to the current conversation.

For example:

.. code-block:: python

    @assist.action('give-diet')
    def set_user_diet(diet):
        speech = 'Are you trying to make food or get food?'
        context_manager.add(diet)
        return ask(speech)

    @assist.context('vegetarian')
    @assist.action('get-food')
    def suggest_food():
        return tell("There's a farmers market tonight.")

    @assist.context('carnivore')
    @assist.action('get-food')
    def suggest_food():
        return tell("Bob's BBQ has some great tri tip")

    @assist.context('broke')
    @assist.action('get-food')
    def suggest_food():
        return tell("Del Taco is open late")



Example
=======

Let's edit the `choose-order-type` action function from the :doc:`quick_start` to set a context


.. code-block:: python

    from flask_assistant import context_manager

    @assist.action('choose-order-type')
    def set_order_context(order_type):
        speech = "Did you say {}?".format(order_type)
        context_manager.add(order_type)
        return ask(speech) 


Now we'll use the incoming context to match a single intent to one of two action functions depending on their required contexs.
The following set of actions represent a branching of the dialogue into two seperate contexts: delivery or pickup

.. The following confirm actions will then be matched depending on the order_type context provided from the previous action

.. code-block:: python

    # will be matched if user said 'pickup'
    @assist.context("pickup")
    @assist.action('confirm')
    def confirm_pickup(answer):
        if 'no' in answer:
            order_type_prompt()
        else:
            speech = "Awesome, would you like to pick up a specialty or custom pizza?"
            context_manager.add('build')
            return ask(speech)

A conversation specific to the 'pickup' context won't require any delivery address information, so the above action adds a 'build' context to transition to the next state of the dialogue: building the pizza

However, the 'delivery' conversation will require this information, so it sets a 'delivery-info' context so that the assistant will prompt for the required delivery information before proceeding to building the pizza.


.. code-block:: python

    # will be matched if user said 'delivery'
    @assist.context("delivery")
    @assist.action('confirm')
    def confirm_delivery(answer):
        if 'no' in answer:
            order_type_prompt()
        else:
            speech = "Ok sounds good. Can I have your address?"
            context_manager.add('delivery-info')
            return ask(speech)


.. tip:: There are a few ways to access and set contexts and their parameters.



    .. code-block:: python

        # get a context object
        my_context = contex_manager.get(context_name)

        # set value directly onto context object
        my_context.set('param1', )



.. Storing Paramater Values in Contexts
.. ====================================

.. We can also use the `context_manager` to store and retrieve values required at later actions.

.. .. code-block:: python
    
..     # set the param directly using the context object
..     my_context = context_manager.get(context_name)
..     my_context.set(param_name, value)

..     # or set the param through the context manager
..     context_manager.set(context_name, param_name, value)



.. For example we can store a value for the number of toppings on a custom pizza.

.. .. code-block:: python

..     @assist.context('custom')
..     @assist.action('add_toppings')
..     def store_value(num_toppings):
..         charge = (num_toppings * .75) / 100
..         context_manager.set('custom', 'num_toppings', num_toppings)
..         speech = '{} toppings will cost {}. Is that ok?'.format(num_toppings, charge)
..         return ask(speech)

.. Later, we can retrieve the parameter value

.. @assist.context('custom', 'checkout')
.. @assist.action('finish-order')
.. def give_total():


.. context_manager.get('finish=checkout')










.. Note that each action also added a new context, which can be used in conjuction with existing contexts to provide more precise intent mapping.


.. For example, imagine that later in the dialogue we want give the user the total price of their pizza. This will depend on which contexts have been activated:
..     - pickup or delivery
..     - custom or specialty pizza
..     - number of toppings (only applicable to custom pizzas)
      
.. Calculating the price could be accomplished like this:

.. @assist.contex('pickup', 'custom' )
.. @assist.action('get-price')
.. def calc_price():


