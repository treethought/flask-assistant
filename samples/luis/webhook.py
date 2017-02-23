import logging
from flask import Flask
from flask_assistant import Bot


app = Flask(__name__)
bot = Bot(app)
logging.getLogger('flask_assistant').setLevel(logging.DEBUG)


@bot.action('None')
def no_match():
    speech = 'Sorry what was that?'
    return bot.connector.reply(speech)


@bot.action('GetMeasure', mapping={'column': 'Column', 'datetime': 'builtin.datetime'})
def measure(column, Filter=None, Status=None, datetime=None, Calculation=None, ):

    speech = 'Measuring {} for column:{} filter:{} status:{} datetime:{}'.format(Calculation, column, Filter, Status, datetime) # {} with datetime {}'.format(column, datetime)
    return  bot.connector.reply(speech)


@bot.action('Select')
def select(Column, Filter=None, Status=None, datetime=None):
    speech = 'Getting {} {}s filtered by {} {}'.format(Status, Column, Filter, datetime=None)
    return  bot.connector.reply('Selecting...')

if __name__ == '__main__':
    app.run(debug=True)
