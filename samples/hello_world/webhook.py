import logging
from flask import Flask
from flask_assistant import Assistant, ask, tell, context_manager, permission, event

app = Flask(__name__)
assist = Assistant(app)
logging.getLogger("flask_assistant").setLevel(logging.DEBUG)

app.config["INTEGRATIONS"] = ["ACTIONS_ON_GOOGLE"]


@assist.action("greeting")
def greet_and_start():
    speech = "Hey! Are you male or female?"
    resp = ask(speech)
    resp.suggest("Male", "Female")
    return resp


@assist.prompt_for("gender", "give-gender")
def prompt_gender(gender):
    return ask("I need to know your gender")


@assist.action("give-gender")
def ask_for_color(gender):
    if gender.lower() == "male":
        gender_msg = "Sup bro!"

    else:
        gender_msg = "Haay gurl!"

    speech = gender_msg + " What is your favorite color?"
    return ask(speech)


@assist.prompt_for("color", intent_name="give-color")
def prompt_color(color):
    speech = "Sorry I didn't catch that. What color did you say?"
    return ask(speech)


@assist.action("give-color", mapping={"color": "sys.color"})
def repeat_color(color):
    speech = "Ok, {} is an okay color I guess.".format(color)
    speech += "\n What pizza do you want"
    return ask(speech)


if __name__ == "__main__":
    app.run(debug=True)
