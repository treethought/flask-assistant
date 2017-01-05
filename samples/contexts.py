import logging
from flask import Flask, request, Response, jsonify, json, make_response
from flask_assistant import Assistant, statement, Context


app = Flask(__name__)
assist = Assistant(app)
logging.getLogger('flask_assistant').setLevel(logging.DEBUG)

### Context Independent actions ###
@assist.action('greetings')
def greetings():
    speech = """We've got some bumpin pies up in here!.
                Would you like to order a Custom or Specialty pizza?"""
    return statement(speech)

# TODO fill params from contexts, so actions can be called and use any context

# Represents the first branching of contexts -> special or custom
@assist.action('begin-order')
def begin_and_set_type(pizza_type):
    if pizza_type == 'custom':
        speech = "Ok, what size custom pizza would you like?"
        custom = Context('custom', lifespan=10)
        custom.set('pizza_type', pizza_type)
        return statement(speech).add_context(custom)

    else:
        speech = 'Cool, do you want to hear a list of our specialties?'
        special = Context('special', lifespan=10)
        special.set('pizza_type', pizza_type)
        return statement(speech).add_context(special)


@assist.context('special')
@assist.action('special-listing')
def list_specials(answer):
    if answer.lower() in 'yes':
        speech = 'We have Canadian bacon with pineapple, meat lovers, and vegetarian. Which one would you like?'
    else:
        speech = 'Ok, you must be a regular. Which pizza do you want?'
    return statement(speech)


@assist.context('special')
@assist.action('special-set-choice')
def set_special_choice(specialty):
    speech = 'Cool, you chose the {} pizza. What size do you want?'.format(specialty)
    special = Context('special')
    special.set('specialty', specialty)

    return statement(speech).add_context(special)

@assist.action('set-size')
def set_size(size, pizza_type, specialty=None):
    if specialty:
        pizza_type = specialty
    speech = 'Ok, so you want a {} {} pizza. Is this correct?'.format(size, pizza_type)
    confirm = Context('confirm', lifespan=1) # set context for confirming order
    return statement(speech).add_context(confirm)

@assist.context('confirm')
@assist.action('confirm-size-type')
def confirm_and_continue(answer):
    if answer.lower() in 'yes':
        speech = 'Awesome, want to add any toppings?'

    else:
        speech = 'Oh ok, did we have the toppings correct?'

    return statement(speech)



if __name__ == '__main__':
    app.run(debug=True)
