# Flask-assistant
### A framework to develop assistants for Google Actions

 Flask-assistant is an easy way to build a API.AI webhook for integration with Google Actions/Home

 This project is heavily inspired and based on John Wheeler's [Flask-ask](https://github.com/johnwheeler/flask-ask) for the Alexa Skills Kit.

 Currently only a very bare-bones implementation allowing for basic integration




#### The aim for Flask-actions is to provide a simple way to develop "assitants" for Google Actions (for use with Google Home).



#### Getting Started
##### A Minimal Assistant

```python
from flask import Flask, request, Response, jsonify, json, make_response
from flask_assistant import Assistant, _Response

app = Flask(__name__)
assistant = Agent(app)
logging.getLogger('flask_assistant').setLevel(logging.DEBUG)

@assistant.action(intent_name='Demo')
def test():
    msg = 'Microphone check 1, 2 what is this?'
    resp = _Response(msg)
    return resp

if __name__ == '__main__':
    app.run(debug=True)
```

##### Accepting parameters
```python
@assistant.action(intent_name='SayColorName, mapping={'name': 'given-name'})
def send_message(name, color):
"""Action is carried out if both parameters are provided"""
    speech = 'Your name is {}'.format(name)
    return _Response(speech)
```

##### Provide prompts for missing paremters required to carry out an action
```python
@assistant.prompt_for(next_param='name')
def prompt_for_name():
    speech = "What is your name?"
    return _Response(speech)

@assistant.prompt_for(next_param='color')
def prompt_for_color():
    speech = "I need your color"
    return _Response(color)
```










