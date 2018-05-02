"""Unit test some basic response rendering functionality.

These tests use the unittest.mock mechanism to provide a simple Assistant
instance for the _Response initialization.
"""
from flask import Flask
from flask_assistant import Assistant
from flask_assistant.response import _Response
import pytest

patch = pytest.importorskip('unittest.mock.patch')


@patch('flask_assistant.response.current_app')
def test_response_with_speech(mock):
    mock = Assistant(Flask(__name__))
    resp = _Response('foobar')
    assert resp._response['speech'] == 'foobar'


@patch('flask_assistant.response.current_app')
def test_response_with_None_speech(mock):
    mock = Assistant(Flask(__name__))
    resp = _Response(None)
    assert resp._response['speech'] is None


@patch('flask_assistant.response.current_app')
def test_response_speech_escaping(mock):
    mock = Assistant(Flask(__name__))
    resp = _Response('foo & bar')
    assert resp._response['speech'] == 'foo &amp; bar'
