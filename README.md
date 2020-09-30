Create Virtual Assistants with Python
=====================================

[![image](https://img.shields.io/pypi/v/flask-assistant.svg)](https://pypi.python.org/pypi/flask-assistant)
[![image](https://travis-ci.org/treethought/flask-assistant.svg?branch=master)](https://travis-ci.org/treethought/flask-assistant) ![image](https://img.shields.io/badge/python-3.5,%203.6,%203.7-blue.svg) [![image](https://img.shields.io/badge/discord-join%20chat-green.svg)](https://discord.gg/m6YHGyJ)

A flask extension serving as a framework to easily create virtual assistants using [Dialogflow](https://dialogflow.com/docs) which may be integrated
with platforms such as [Actions on
Google](https://developers.google.com/actions/develop/apiai/) (Google
Assistant).

Flask-Assistant allows you to focus on building the core business logic
of conversational user interfaces while utilizing Dialogflow's Natural
Language Processing to interact with users.

**Now supports Dialogflow V2!**

This project is heavily inspired and based on John Wheeler's
[Flask-ask](https://github.com/johnwheeler/flask-ask) for the Alexa
Skills Kit.

Features
--------

> - Mapping of user-triggered Intents to action functions
> - Context support for crafting dialogue dependent on the user's requests
> - Define prompts for missing parameters when they are not present in the users request or past active contexts
> - A convenient syntax resembling Flask's decoratored routing
> - Rich Responses for Google Assistant

Hello World
-----------

```python
from flask import Flask
from flask_assistant import Assistant, ask

app = Flask(__name__)
assist = Assistant(app, project_id="GOOGLE_CLOUD_PROJECT_ID")

@assist.action("Demo")
def hello_world():
    speech = "Microphone check 1, 2 what is this?"
    return ask(speech)

if __name__ == "__main__":
    app.run(debug=True)
```

How-To
------

> 1.  Create an Assistant object with a Flask app.
> 2.  Use action decorators to map intents to the
>     proper action function.
> 3.  Use action view functions to return ask or tell responses.

Documentation
-------------

-   Check out the [Quick
    Start](http://flask-assistant.readthedocs.io/en/latest/quick_start.html)
    to jump right in
-   View the full
    [documentation](http://flask-assistant.readthedocs.io/en/latest/)
