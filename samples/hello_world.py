import logging

from flask import Flask, request, Response, jsonify, json, make_response
from flask_actions import Agent, _Response
from pprint import pprint



app = Flask(__name__)
agent = Agent(app)
logging.getLogger('flask_actions').setLevel(logging.DEBUG)


@agent.intent('Demo')
def test():
    msg = 'Microphone check 1, 2 what is this?'
    resp = _Response(msg)
    return resp

if __name__ == '__main__':
    app.run(debug=True)
