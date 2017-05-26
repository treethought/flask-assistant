import logging
from flask import Flask
from flask_assistant import Assistant, ask, tell, build_item


app = Flask(__name__)
assist = Assistant(app)
logging.getLogger('flask_assistant').setLevel(logging.DEBUG)


app.config['INTEGRATIONS'] = ['ACTIONS_ON_GOOGLE']


@assist.action('Default Welcome Intent')
def welcome():
    speech = 'Welcome to Flask-Assistant on the Google Assistant! Wanna see what I can do?'
    return ask(speech).reprompt('Do you want to see some examples?')


@assist.action('Default Welcome Intent - yes')
def action_func():
    speech = """This is just a simple text to speech message, not too impressive.
                Ask to see a card!"""

    return ask(speech).suggest('Show card', 'Show List')


@assist.action('ShowCard')
def show_card():
    title = 'A Simple Card'
    img_url = "http://flask-assistant.readthedocs.io/en/latest/_static/logo-xs.png"

    text = """Flask-Assistant allows you to focus on building the core business logic
                of conversational user interfaces while utilizing API.AI’s
                Natural Language Processing to interact with users."""

    speech = 'Now ask to see a list...'

    resp = ask(speech)
    resp.card(text, title, img_url)
    resp.suggest('Show List')

    return resp


@assist.action('ShowList')
def action_func():

    #Build items independent of list
    items = []
    for i in range(4,10):
        title = 'Item {}'.format(i)
        key = str(i)
        items.append(build_item(title, key))

    resp = ask("Here's an example of a list selector")
    mylist = resp.build_list('Cool Projects')  # passes the speech paramter to new class


    mylist.add_item('Flask-Assistant', key='flask_assistant', img_url="http://flask-assistant.readthedocs.io/en/latest/_static/logo-xs.png")
    mylist.add_item('Flask-Ask', key='flask_ask')
    mylist.add_item('Alphabets', key='alphabets')

    # include built items in list
    mylist.include_items(items).link_out('GitHub Repo', 'https://github.com/treethought/flask-assistant')

    return mylist


@assist.action('FlaskAssistantCarousel')
def action_func():
    resp = tell('Heres some info on Flask-Assistant').build_carousel()
    resp.add_item('Title', key='title', description='Here is a Description')
    resp.add_item('Title2', key='title2', description='Here is another descriotion')
    return resp

@assist.action('ShowCarousel')
def action_func():
    mycarousel = carousel(speech='Here is a carousel',
                          title='A sample carousel')
    mycarousel.add_item(
        'Option A', 'Key1', img_url="http://flask-assistant.readthedocs.io/en/latest/_static/logo-xs.png")
    mycarousel.add_item('Option B', 'Key2')
    return mycarousel


@assist.action('ShowSuggestion')
def action_func():
    speech = 'Try these sugeestions'
    return suggest(speech, ['a', 'b', 'c'])


if __name__ == '__main__':
    app.run(debug=True)
