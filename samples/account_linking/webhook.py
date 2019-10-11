from flask import Flask
from flask_assistant import Assistant, ask, profile, sign_in


app = Flask(__name__)

app.config['INTEGRATIONS'] = ['ACTIONS_ON_GOOGLE']
app.config['AOG_CLIENT_ID'] =  "CLIENT_ID OBTAINED BY SETTING UP ACCOUNT LINKING IN AOG CONSOLE"


assist = Assistant(app=app, route="/", project_id="YOUR_GCP_PROJECT_ID")

@assist.action("Default Welcome Intent")
def welcome():
    if profile:
        return ask(f"Welcome back {profile['name']}")

    return sign_in("To learn more about you")

# this intent must have the actions_intent_SIGN_IN event
# and will be invoked once the user has 
@assist.action("Complete-Sign-In")
def complete_sign_in():
    if profile:
        return ask(f"Welcome aboard {profile['name']}, thanks for signing up!")
    else:
        return ask("Hope you sign up soon! Would love to get to know you!")


if __name__ == "__main__":
    app.run(debug=True)

