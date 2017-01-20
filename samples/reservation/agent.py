import logging
from flask import Flask
from flask_assistant import Assistant, ask, tell, context_manager


app = Flask(__name__)
assist = Assistant(app)
logging.getLogger('flask_assistant').setLevel(logging.DEBUG)


@assist.action('welcome')
def welcome():
    speech = """Welcome to Booking McBookface Adventures.
                do you want to travel via plane, train, or automobile?
            """
    return ask(speech)


@assist.action('declare-transport')
def transport_method(transport):
    # set context to hold all trip info
    trip = context_manager.add('trip').set('transport', transport)

    # parameters can also be stored in context as dictionary keys
    trip['transport'] = transport

    speech = " Ok, you chose {} right?".format(transport)
    return ask(speech)


@assist.context('trip')
@assist.action('confirm')
def confirm_transport(answer):
    if 'n' in answer:
        return ask('I dont think I understood. What transportation do you want to take?')
    else:
        return ask('Ok, is this going to be a one-way trip or round ticket?')


# view_function parameters, if not provided with the user's query,
# will be accessed from reviously declared contexts
@assist.context('trip')
@assist.action('delcare-ticket-type')
def oneway_or_round(ticket_type, transport):
    context_manager.add(ticket_type)  # set context for one way/round trip dialogues
    context_manager.add('departure')
    speech = 'Cool, what city do you want to leave from for your {} {} trip?'.format(ticket_type, transport)
    return ask(speech)


@assist.context('departure')
@assist.action('give-city')
def departure_location(city):
    context_manager.set('departure', 'city', city)
    return ask('What day would you like to leave?')


@assist.context('departure')
@assist.action('give-day')
def departure_date(day):
    context_manager.set('departure', 'day', day)
    context_manager.add('arrival')
    speech = 'Ok would you like to confrim your booking details?'
    return ask(speech)

@assist.context('arrival')
@assist.action('give-city')
def get_destination(city):
    context_manager.set('arrival', 'city', city)
    speech = 'Would you like to book a room at the McHotelFace hotel in {}?'.format(city)
    return ask(speech)

@assist.context('arrival')
@assist.action('book-hotel')
def book_hotel(answer):
    context_manager.set('arrival', 'book_hotel', answer)
    if 'y' in answer:
        hotel_speech = 'Ok, your room will be ready for you.'
    else:
        hotel_speech = 'No hotel needed, got it.'





@assist.context('departure', 'one-way')
@assist.action('confirm')
def confirm_one_way_details(answer, transport, ticket_type, city, date):
    if 'y' in answer:
        speech = "I have you set for a {} {} trip. You will be leaving from {} on {} and you will never return!"
        return tell(speech)

# @assist.context('return', 'round')
# @assist.action('give-city')
# def return_location(city):

