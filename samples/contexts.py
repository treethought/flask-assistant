import logging
from flask import Flask, request, Response, jsonify, json, make_response
from flask_assistant import Assistant, statement, Context


app = Flask(__name__)
assist = Assistant(app)
logging.getLogger('flask_assistant').setLevel(logging.DEBUG)


@assist.action(intent_name='greetings')
def greetings():
    speech = """We've got some bumpin pies up in this bitch!.
                Would you like to order a Custom or Specialty pizza?"""

    return statement(speech)


# @context('custom')
@assist.action(intent_name="custom")
def custom_size():
    speech = "Ok, Do you want a small 8 or a large 16 inch custom pizza?"
    out_context = Context('custom').serialize

    return statement(speech).context_out(out_context)

@assist.action(intent_name='custom-toppings', in_context='custom')
def choose_toppings(size):
    num_toppings = 2
    if size in 'large16sixteen':
        num_toppings = 4

    speech = "Ok, the {} inch pizza comes with {} toppings. Which toppings would you like?".format(size, num_toppings)
    out_context = Context('custom', parameters={'size': size, 'num_toppins': num_toppings})

    return statement(speech).context_out(out_context)






if __name__ == '__main__':
    app.run(debug=True)
