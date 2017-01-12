import logging
from flask import Flask
from flask_assistant import Assistant, ask, tell, Context


app = Flask(__name__)
assist = Assistant(app)
logging.getLogger('flask_assistant').setLevel(logging.DEBUG)


@assist.action('greetings')
def greetings():
    speech = """We've got some bumpin pies up in here!.
                Would you like to order for pickup or delivery?"""
    select_method = Context('select-method', lifespan=1)
    return ask(speech).add_context(select_method)


def reprompt_method():
    return ask('Sorry, is this order for pickup or delivery?')


# Represents the first branching of contexts -> delivery or pickup
@assist.context("select-method")
@assist.action('choose-order-method')
def make_sure(order_method):
    method_context = Context(order_method)
    speech = "Did you say {}?".format(order_method)
    return ask(speech).add_context(method_context)


# Delivery context actions to gather address info

@assist.context("delivery")
@assist.action('confirm')
def confirm_delivery(answer):
    if 'n' in answer:
        reprompt_method()
    else:
        speech = "Ok sounds good. Can I have your address?"
        context_out = Context('delivery-info')
        return ask(speech).add_context(context_out)


@assist.context("delivery", "delivery-info")
@assist.action('store-address')
def store_address(address):
    speech = "Ok, and can I have your name?"

    info = Context('delivery-info', lifespan=10)  # keep alive for end of order
    info.set('address', address)

    return ask(speech).add_context(info)


@assist.context("delivery", "delivery-info")
@assist.action('store-name')
def store_phone(name, address):  # address can be pulled from existing delivery-info context
    speech = """Thanks, {} ... Ok, that's all I need for your delivery info.
        With your address being {}, delivery time should be about 20 minutes.
        So would you like a special or custom pizza?""".format(name, address)

    info = Context('delivery-info', lifespan=10)  # keep alive for end of order
    info.set('name', name)

    ready_to_build = Context('build')

    return ask(speech).add_context(info, ready_to_build)


@assist.context("pickup")
@assist.action('confirm')
def confirm_pickup(answer):
    if 'y' in answer:
        speech = "Awesome, let's get your order started. Would you like a custom or specialty pizza?"
        ready_to_build = Context("build")
        return ask(speech).add_context(ready_to_build)
    else:
        reprompt_method()


@assist.context('build')
@assist.action('begin-order')
def begin_and_set_type(pizza_type):
    if pizza_type == 'custom':
        speech = "Ok, what size custom pizza would you like?"
    else:
        speech = 'We have Canadian bacon with pineapple, meat lovers, and vegetarian. Which one would you like?'
        pizza_type = 'special'

    # Store pizza details throughout order
    pizza = Context('pizza', lifespan=10)
    pizza.set('type', pizza_type)

    # Set context for which questions you will ask about the pizza
    # either 'custom' or 'special'
    type_context = Context(pizza_type)
    return ask(speech).add_context(pizza, type_context)


@assist.context('build', 'special')
@assist.action('choose-special-type')
def set_special_choice(specialty):
    speech = 'Cool, you chose a {} pizza. What size do you want?'.format(specialty)
    special = Context('special')
    special.set('specialty', specialty)

    return ask(speech).add_context(special)

# This action is matched for the set-size intent regardless of pizza-type context
# action params are matched to the corresponding parameter within existing contexts
# if not provided with user's response


@assist.context('build')
@assist.action('set-size')
def set_size(size, pizza_type, specialty=' '):
    speech = 'Ok, so you want a {} {} {} pizza. Is this correct?'.format(size, specialty, pizza_type)
    size_chosen = Context('size-chosen', lifespan=1)  # set context for confirming order
    return ask(speech).add_context(size_chosen)


@assist.context('custom', 'size-chosen')
@assist.action('confirm')
def confirm_and_continue(answer):
    if answer.lower() in 'yes':
        speech = 'Awesome, what topping would you like to add first? We have pepperoni, bacon, and veggies.'
        toppings = Context('toppings', lifespan=4)
        return ask(speech).add_context(toppings)

    else:
        return review_pizza()


@assist.context('build', 'toppings')
@assist.action('choose-toppings')
def store_toppings(new_topping):
    speech = 'Ok, I added {} to your pizza. Add another?'.format(new_topping)
    toppings = Context('toppings')
    toppings.set('top1', new_topping)
    return ask(speech).add_context(toppings)




if __name__ == '__main__':
    app.run(debug=True)
