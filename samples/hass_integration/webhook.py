import logging
from flask import Flask
from flask_assistant import Assistant, tell
from flask_assistant.hass import HassRemote

app = Flask(__name__)
assist = Assistant(app)
hass = HassRemote('Your Home Assistant Password')
logging.getLogger('flask_assistant').setLevel(logging.DEBUG)



@assist.action('greeting')
def welcome():
    speech = 'Heres an exmaple of Home Assistant integration'
    hass.call_service('script', 'flash_lights')
    return tell(speech)

@assist.action('get-light-states')
def light_report():
    speech = ''
    for light in hass.light_states:
        speech += '{} is {} '.format(light.object_id, light.state)
    return tell(speech)


@assist.action('turn-on-light')
def turn_on_light(light, brightness=255):
    speech = 'Turning on {} to {}'.format(light, brightness)
    hass.turn_on_light(light, brightness)
    return tell(speech)

@assist.action('turn-off-light')
def turn_off_light(light):
    speech = 'Turning off {}'.format(light)
    hass.turn_off_light(light)
    return tell(speech)


@assist.action('toggle-switch')
def switch(switch):
    speech = 'Toggling switch for {}'.format(switch)
    hass.switch(switch)
    return tell(speech)


@assist.action('start-script')
def run_script(script):
    speech = 'Running {}'.format('script.{}'.format(script))
    hass.start_script(script)
    return tell(speech)

@assist.action('run-command')
def run(shell_command):
    speech = 'Running the {} command shel command'.format(shell_command)
    hass.command(shell_command)
    return tell(speech)


if __name__ == '__main__':
    app.run(debug=True)



