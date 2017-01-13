# Flask-assistant
### A flask extension for developing assistants for Google Home / Google Actions

 Flask-assistant is an easy way to build a backend webhook for API.AI with integration for Google Actions

 This project is heavily inspired and based on John Wheeler's [Flask-ask](https://github.com/johnwheeler/flask-ask) for the Alexa Skills Kit.

 Currently only a very bare-bones implementation allowing for basic integration







#### Getting Started
`pip install flask-assistant`

##### A Minimal Assistant

```python
from flask import Flask
from flask_assistant import Assistant, ask, tell

app = Flask(__name__)
assistant = Assistant(app)
logging.getLogger('flask_assistant').setLevel(logging.DEBUG)

@assistant.action(intent_name='Demo')
def test():
    speech = 'Microphone check 1, 2 what is this?'
    return tell(speech)

if __name__ == '__main__':
    app.run(debug=True)
```

##### Accepting parameters
```python
@assistant.action(intent_name='SayColorName')
def send_message(name, color):
"""Action is carried out if both parameters are provided"""
    speech = 'Your name is {} and your color is {}'.format(name, color)
    return tell(speech)
```

##### Provide prompts for missing paremters required to carry out an action
```python
@assistant.prompt_for(next_param='name')
def prompt_for_name():
    speech = "What is your name?"
    return ask(speech)

@assistant.prompt_for(next_param='color')
def prompt_for_color():
    speech = "I need your color"
    return ask(speech)
```

##### Use contexts to map intents to different actions to build a dialogue 
```python
@assistant.action('greetings')
def greetings():
    speech = """We've got some bumpin pies up in here!
                Would you like to order for pickup or delivery?"""
    return ask(speech)

def method_reprompt():
    return ask('Sorry, is this order for pickup or delivery?')

# Represents branching of contexts -> delivery or pickup order method
@assist.context("method")
@assist.action('choose-order-method')
def set_method(order_method):
    speech = "Did you say {}?".format(order_method)
    context_manager.add(order_method, lifespan=10) # provide a context-out to guide dialogue
    return ask(speech) 


# The following actions will be matched depending
# on the order method context provided from the previous action
@assist.context("pickup")
@assist.action('confirm')
def confirm_pickup(answer):
    if 'n' in answer:
        method_reprompt()
    else:
        speech = "Awesome, let's get your order started. Would you like a custom or specialty pizza?"
        context_manager.add('build')
        return ask(speech)


@assist.context("delivery")
@assist.action('confirm')
def confirm_delivery(answer):
    if 'n' in answer:
        method_reprompt()
    else:
        speech = "Ok sounds good. Can I have your address?"
        context_manager.add('delivery-info')
        return ask(speech)
```


### Testing and Development
##### With API.AI as the middleman, getting an assistant up and running for the development very simple
##### You will need to register an API.AI agent and a Google Project

+ Create an [API.AI agent](https://console.api.ai/api-client/#/newAgent)
    - Click on Fullfillment in the left side menu
    - Enable Webhook
    - Provide the URL to the route provided to the Assitant class constructor
        - Your assitant app serves as the webhook and needs to be publically available at this url
        - This can be easily done using [ngrok](https://ngrok.com/)

+ Create a new intent

    - Enter some sample user expressions
    - Provide an action name corresponding to your intent's action function within your assistant app
    - Declare any parameters to be parsed and delivered from speech commands to your assistant
        - Mark as required if they are required for the action function.

    - Click the 'Fulfillment' heading underneath 'Add Message Content'
        - Enable 'Use Webhook'
        - Enable 'Use webhook for slot-filling' if you wish to provide parameter prompts from your webhook

    - Save the intent

+ Integrate API.AI Agent with Google Actions

    - Click 'Integrations' in the left side menu
    - Toggle 'Actions on Google'
    - Click Settings
        - Provide the necessary details
        - Click Authorize and then preview

##### You should now be able to send requests to your assistant using voice or text commands from 
- the [API.AI console](https://console.api.ai/api-client/) for quick testing, or
- the [Google Home Web Simulator](https://developers.google.com/actions/tools/web-simulator) to test from the Google Home user endpoint












