import logging
from flask import Flask
from flask_assistant import Assistant, ask, tell, context_manager, Bot


app = Flask(__name__)
bot = Bot(app)
logging.getLogger('flask_assistant').setLevel(logging.DEBUG)


@bot.action('None')
def no_match():
    speech = 'Sorry what was that?'
    return ask(speech)

if __name__ == '__main__':
    app.run(debug=True)



