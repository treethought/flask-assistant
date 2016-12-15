import logging

from flask import Flask, request, Response, jsonify, json, make_response
from flask_assistant import Agent, _Response



app = Flask(__name__)
assistant = Agent(app)
logging.getLogger('flask_assistant').setLevel(logging.DEBUG)


@assistant.intent('Demo')
def test():
    msg = 'Microphone check 1, 2 what is this?'
    resp = _Response(msg)
    return resp


@assistant.intent(intent_name='0-SendMessage', mapping={'name': 'given-name'})
def send_message(name, message):
    """Builds a Message and confirms it if both parameters are provided"""
    speech = 'Sending {} to {}. Is that correct?'.format(message, name)
    return _Response(speech)


@assistant.fill_slot(intent_name='0-SendMessage', next_param='given-name')
def prompt_for_name():
    speech = 'Who should I send the message to dawg?'
    return _Response(speech)


@assistant.fill_slot(intent_name='0-SendMessage', next_param='message')
def prompt_for_message():
    speech = 'What should the message say, my brotha?'
    return _Response(speech)


if __name__ == '__main__':
    app.run(debug=True)
