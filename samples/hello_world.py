import logging
from flask import Flask
from flask_assistant import Assistant, ask, tell

app = Flask(__name__)
assistant = Assistant(app)
logging.getLogger('flask_assistant').setLevel(logging.DEBUG)


@assistant.action('Demo')
def test():
    msg = 'Microphone check 1, 2 what is this?'
    return tell(msg)


@assistant.action(intent='0-SendMessage', mapping={'name': 'given-name'})
def send_message(name, message):
    """Builds a Message and confirms it if both parameters are provided"""
    speech = 'Sending {} to {}. Is that correct?'.format(message, name)
    return ask(speech)


@assistant.prompt_for(next_param='given-name', intent='0-SendMessage')
def prompt_for_name():
    speech = 'Who should I send the message to dawg?'
    return ask(speech)


@assistant.prompt_for(next_param='message', intent='0-SendMessage')
def prompt_for_message():
    speech = 'What should the message say, my brotha?'
    return ask(speech)

@assistant.action('SendMessage')
def send_message():
    return tell('Cool, sending the message')

if __name__ == '__main__':
    app.run(debug=True)
