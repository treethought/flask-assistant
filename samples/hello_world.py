import logging
from flask import Flask, request, Response, jsonify, json, make_response
from flask_assistant import Assistant, statement

app = Flask(__name__)
assistant = Assistant(app)
logging.getLogger('flask_assistant').setLevel(logging.DEBUG)


@assistant.action('Demo')
def test():
    msg = 'Microphone check 1, 2 what is this?'
    resp = _Response(msg)
    return resp


@assistant.action(intent_name='0-SendMessage', mapping={'name': 'given-name'})
def send_message(name, message):
    """Builds a Message and confirms it if both parameters are provided"""
    speech = 'Sending {} to {}. Is that correct?'.format(message, name)
    return statement(speech)


@assistant.prompt_for(next_param='given-name', intent_name='0-SendMessage')
def prompt_for_name():
    speech = 'Who should I send the message to dawg?'
    return statement(speech)


@assistant.prompt_for(next_param='message', intent_name='0-SendMessage')
def prompt_for_message():
    speech = 'What should the message say, my brotha?'
    return statement(speech)


if __name__ == '__main__':
    app.run(debug=True)
