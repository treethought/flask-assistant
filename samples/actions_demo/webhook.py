import logging
from flask import Flask
from flask_assistant import Assistant, ask, card, carousel, list_selector, simple, suggest, context_manager as manager


app = Flask(__name__)
assist = Assistant(app)
logging.getLogger('flask_assistant').setLevel(logging.DEBUG)


@assist.action('Default Welcome Intent')
def welcome():
    speech = 'Welcome to Flask-Assistant on the Google Assistant! Wanna see what I can do?'
    return simple(speech)




@assist.action('Default Welcome Intent - yes')
def action_func():
    speech = """This is just a simple text to speech message, not too impressive.
                Ask to see a card!"""
    return simple(speech)

@assist.action('ShowCard')
def show_card():
    title = 'A Simple Card'
    img_url = "http://flask-assistant.readthedocs.io/en/latest/_static/logo-xs.png"

    text = """Flask-Assistant allows you to focus on building the core business logic
                of conversational user interfaces while utilizing API.AI’s
                Natural Language Processing to interact with users."""

    speech = 'Now ask to see a list...'

    return card(speech, text, title, img_url)


@assist.action('ShowList')
def action_func():
    mylist = list_selector(speech='Here is a list', title='My Sample List')
    mylist.add_item('Option A', 'Key1', img_url="http://flask-assistant.readthedocs.io/en/latest/_static/logo-xs.png")
    mylist.add_item('Option B', 'Key2')
    return mylist

@assist.action('ShowCarousel')
def action_func():
    mycarousel = carousel(speech='Here is a carousel', title='A sample carousel')
    mycarousel.add_item('Option A', 'Key1', img_url="http://flask-assistant.readthedocs.io/en/latest/_static/logo-xs.png")
    mycarousel.add_item('Option B', 'Key2')
    return mycarousel

@assist.action('ShowSuggestion')
def action_func():
    speech = 'Try these sugeestions'
    return suggest(speech, ['a', 'b', 'c'])


if __name__ == '__main__':
    app.run(debug=True)
