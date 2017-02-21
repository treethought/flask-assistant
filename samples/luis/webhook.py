import logging
from flask import Flask
from flask_assistant import Bot


app = Flask(__name__)
bot = Bot(app)
logging.getLogger('flask_assistant').setLevel(logging.DEBUG)


@bot.action('None')
def no_match():
    speech = 'Sorry what was that?'
    return bot.connector.reply(speech')


@bot.action('GetMeasure')
def measure():
    return  bot.connector.reply('Getting Measure')


@bot.action('Select')
def select():
    return  bot.connector.reply('Selecting...')

if __name__ == '__main__':
    app.run(debug=True)
