************************************
Home Assistant Integration
************************************

Flask-Assistant includes a :class:`HassRemote <flask_assistant.HassRemote>` interface to make requests to Home Assistant's `REST api <https://home-assistant.io/developers/rest_api/>`_. This allows your Dialogflow agent to control and retrieve data about your IoT devices.



Integrating your assistant with Home Assistant is as easy as adding a method call to your action functions.


Using the HassRemote
=====================


First import and create an instance of the HassRemote.

.. code-block:: python

    from flask import Flask
    from flask_assistant import Assistant, tell
    from flask_assistant.hass import HassRemote

    app = Flask(__name__)
    assist = Assistant(app)
    hass = HassRemote('YOUR Home Assistant PASSWORD')

Sending Requests to Home Assistant
----------------------------------


The HassRemote is a simple wrapper around Home Assistant's own `remote <https://github.com/home-assistant/home-assistant/blob/master/homeassistant/remote.py>`_ module. The remote module can be used in the same way to control Home Assistant. ``HassRemote`` just provides a set of methods for commonly sent requests specific to entitiy domain. These methods will often accept the same paramter as the action function itself, allowing clean and more cohesive code within action functions.


.. important:: Each of these methods require the entity_id parameter. The name of this parameter should be the same as  the Home Assistant domain.

    For example:

    If you have a switch in your HA configuration with the name "switch.coffee_maker", the name of the parameter should be "switch". This allows your entities to be properly defined within your entities.yaml template when generating schema.


Controlling Lights
^^^^^^^^^^^^^^^^^^

.. code-block:: python

    @assist.action('turn-on-light')
    def light_on(light, brightness=255):
        speech = 'Turning on {} to {}'.format(light, brightness)
        hass.turn_on_light(light, brightness)
        return tell(speech)

    @assist.action('turn-off-light')
    def light_off(light):
        speech = 'Turning off {}'.format(light)
        hass.turn_off_light(light)
        return tell(speech)


Flip a Switch
^^^^^^^^^^^^^^

.. code-block:: python

    @assist.action('toggle-switch')
    def toggle(switch):
        speech = 'Toggling switch for {}'.format(switch)
        hass.switch(switch)
        return tell(speech)

    @assist.action('switch-on')
    def switch_on(switch):
        speech = 'Flipping on {} switch'.format(switch)
        hass.switch(switch, service='turn_on')
        return tell(speech)


Starting HA Scripts
^^^^^^^^^^^^^^^^^^^

.. code-block:: python

    @assist.action('start-script')
    def start(script):
        speech = 'Running {}'.format('script.{}'.format(script))
        hass.start_script(script)
        return tell(speech)

Running Shell Commands
^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

    @assist.action('run-command')
    def run(shell_command):
        speech = 'Running the {} shell command'.format(shell_command)
        hass.command(shell_command)
        return tell(speech)


.. Controlling Groups
.. ------------------

.. .. code-block:: python

..     @assist.action('turn-on-group')
..     def turn_on_group(group, brightness=255):
..         speech = 'Turning on {} to {} brightness'.format(group, brightness)
..         hass.call_service('light', 'turn_on', {'entity_id': 'group.{}'.format(group), brightness: brightness})
..         return tell(speech)


Hass Entity Templates
======================

Home Assistant devices used within action functions can easily be included in your entries template, and are automatically added with the when :doc:`generating schema <generate_schema>`.


Although Home Assistant and Dialogflow both use the term entities, they are used in slightly different ways.

Home Assistant:
    - uses the term entity to describe any device or service connected to HA.
    - Each entity belongs to a domain (component).

Dialogflow:
    - Uses the term entity to describe a concept that is used within actions
    - Each instance of the entity is called an entry, and may be the value of parameters required by actions

Therefore, the idea of a ``HA entity`` is similar to an ``Dialogflow entry``.

So HA devices can be defined as entries under their domain, with their domain serving as the Dialogflow entity.

    .. code-block:: yaml

        domain:
            - device1: [synonyms]
            - device2: [synonyms]

Template Examples
-----------------

A Group of Lights:
^^^^^^^^^^^^^^^^^^

.. code-block:: yaml

    light:
      - lamp_1: ['ceiling light', 'fan light', 'main light']
      - lamp_2: ['lamp', 'desk lamp']
      - lamp_3: ['bedroom light', 'room light', 'bedroom']
      - room: ['all lights', 'lights', 'room'] # a group within home assistant

    Within Home Assistant lamp_2 would be identified as light.lamp_2 and room as light.room


Switches
^^^^^^^^

.. code-block:: yaml

    switch:
      - coffee_maker: ['coffee', 'brew', 'coffee machine']
      - playstation4: ['ps4', 'playstation']
      - stereo: ['sound', 'sound system']


Scripts
^^^^^^^^

.. code-block:: yaml

    script:
      - flash_lights: ['flash', 'flash the lights', 'strobe']
      - party_mode: ['bump it up', 'start the party']

Shell Commands
^^^^^^^^^^^^^^

.. code-block:: yaml


    shell_command:
      - playstation_netflix_start: ['netflix', 'netflix on the ps4']
      - playstation_overwatch_start: [overwatch]
      - playstation_gtav_start: [gta five, gta]
