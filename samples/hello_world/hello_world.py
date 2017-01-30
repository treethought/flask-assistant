import logging
from flask import Flask
from flask_assistant import Assistant, ask, tell

app = Flask(__name__)
assist = Assistant(app)
logging.getLogger('flask_assistant').setLevel(logging.DEBUG)


@assist.action('Demo')
def test():
    msg = 'Microphone check 1, 2 what is this?'
    return tell(msg)

@assist.action('greetings')
def greetings():
    speech = """Hello, what is your favorite color?"""
    return ask(speech)

@assist.action('give-color')
def echo_color(color):
    speech = "Your favorite color is {}".format(color)
    return tell(speech)

@assist.prompt_for('color', intent='give-color')
def prompt_color(color):
    speech = "Sorry I didn't catch that. What color did you say?"
    return ask(speech)

if __name__ == '__main__':
    app.run()


if __name__ == '__main__':
    app.run(debug=True)
