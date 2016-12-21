from flask import Flask, request, Response, jsonify, json, make_response
from flask_assistant import Assistant, statement, Context
import logging

app = Flask(__name__)
assist = Assistant(app)
logging.getLogger('flask_assistant').setLevel(logging.DEBUG)



@assist.action(intent='greetings')
def greetings():

    speech = """We've got some bumpin pies up in this bitch!. Would you like to order a Custom or Specialty pizza?"""

    return statement(speech)


@assist.action(intent="custom")
def begin_custom():
    speech = "Ok, Do you want a small or a large inch custom pizza?"
    custom = Context('custom')
    return statement(speech).add_context([custom])

@assist.context(['custom', 'pizza'])
@assist.action(intent='custom-size', with_context=['custom'])
def toppings_for_size(size):
    num_toppings = 2
    if size in 'large':
        num_toppings = 4

    speech = "Ok, the {}  pizza comes with {} toppings. What is your first topping?".format(size, num_toppings)
    custom = Context('custom')
    custom.set('size', size)

    # out_context = Context('custom', parameters={'size': size, 'num_toppins': num_toppings})

    return statement(speech).add_context([custom])

@assist.action(intent='custom-add-topping', with_context=['custom'])
def first_topping(topping):
    speech = 'Added {} topping to custom pizza. Whats your second topping?'
    custom = Context(custom)
    custom.set('first_top', topping)

    return statement(speech).add_context([custom])


if __name__ == '__main__':
    app.run(debug=True)
