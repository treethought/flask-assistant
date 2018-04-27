"""Test the response rendering functionality."""

from flask_assistant.response import strip_ssml


def test_ssml_cleanup_necessary():
    rendered = '<sub alias="foobar">hello world</sub>'
    assert strip_ssml(rendered) == 'hello world'


def test_ssml_cleanup_not_necessary():
    rendered = 'hello world'
    assert strip_ssml(rendered) == rendered
