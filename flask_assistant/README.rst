
Create Virtual Assistants with Python
===============================================


A flask extension serving as an `API.AI`_  SDK to provide an easy way to create virtual assistants which may be integrated with platforms such as `Google Actions`_ (Google Home).

.. _`Google Actions`: https://developers.google.com/actions/develop/apiai/ 
.. _`fullfillment`: https://developers.google.com/actions/develop/apiai/dialogs-and-fulfillment#overview
.. _API.AI: https://docs.api.ai/

Flask-Assistant allow you to focus on building the fullfillment_ of actions invoked by the user and desgin a conversational flow to build contextual dialogues.


Features
---------
    - Automatic automatically map user-triggered Intents to action functions
    - Context support for crafting dialogue dependent on the user's requests
    - Define prompts for missing parameters when they are not present in the users request or past active contexs
    - A convenient syntax resembling Flask's decoratored routing
    - Internal API.AI schema generation and registration
      


Hello World
------------

.. code-block:: python

    from flask import Flask
    from flask_assistant import Assistant, tell

    app = Flask(__name__)
    assist = Assistant(app)

    @assist.action('Demo')
    def hello_world():
        speech = 'Microphone check 1, 2 what is this?'
        return tell(speech)

    if __name__ == '__main__':
        app.run(debug=True)


Documentation
--------------

- Check out the :doc:`quick_start` to jump right in
- View the full `documentation <http://flask-assistant.readthedocs.io/en/latest/>`_
  
Contributing
-------------
Help improve flask_assistan by opening an issue

.. _`Quick Start`:
.. _`documentation`: http://flask-assistant.readthedocs.io/en/latest/>


  









