import logging
from flask import Flask, request, Response, jsonify, json, make_response
from flask_assistant import Assistant, statement

app = Flask(__name__)
assistant = Assistant(app)
logging.getLogger('flask_assistant').setLevel(logging.DEBUG)

@assistant.action()