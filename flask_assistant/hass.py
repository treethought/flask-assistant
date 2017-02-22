import homeassistant.remote as remote

class HassRemote(object):
    """Wrapper around homeassistant.remote to make requests to HA's REST api"""

    def __init__(self, password, host='127.0.0.1', port=8123, use_ssl=False):
        self.password = password
        self.host = host
        self.port = port
        self.use_ssl = use_ssl
        self.api = None

        self.connect()

    def connect(self):
        self.api = remote.API(self.host, api_password=self.password, port=self.port, use_ssl=self.use_ssl)
        print('Connecting to Home Assistant instance...')
        print(remote.validate_api(self.api))


    @property
    def _config(self):
        return remote.get_config(self.api)

    @property
    def _event_listeners(self):
        return remote.get_event_listeners

    @property
    def _services(self):
        return remote.get_services(self.api)

    @property
    def _states(self):
        return remote.get_states(self.api)

    @property
    def domains(self):
        return [s['domain'] for s in self._services]

    @property
    def services(self):
        return [s['services'] for s in self._services]

    def get_state(self, entity_id):
        return remote.get_state(self.api, entity_id)

    def set_state(self, entity_id, new_state, **kwargs):
        "Updates or creates the current state of an entity."
        return remote.set_state(self.api, new_state, **kwargs)

    def is_state(self, entity_id, state):
        """Checks if the entity has the given state"""
        return remote.is_state(self.api, entity_id, state)

    def call_service(self, domain, service, service_data={}, timeout=5):
        return remote.call_service(self.api, domain, service, service_data=service_data, timeout=timeout)


    # reports
    @property
    def light_states(self):
        return [i for i in self._states if i.domain == 'light']

    @property
    def sensors(self):
        return [i for i in self._states if i.domain == 'sensor']
    
    # Shortcut service calls
    def switch(self, switch_name, service='toggle'):
        data = {'entity_id': 'script.{}'.format(switch_name)}
        return remote.call_service(self.api, 'switch', service, service_data=data)

    def turn_off_light(self, light_name):
        data = {'entity_id': 'light.{}'.format(light_name)}
        return remote.call_service(self.api, 'light', 'turn_off', service_data=data)

    def turn_on_light(self, light_name, brightness=255):
        data = {'entity_id': 'light.{}'.format(light_name), 'brightness': brightness}
        return remote.call_service (self.api, 'light', 'turn_on', service_data=data)

    # def turn_on_group(self, group_name, **kwargs):
    #     data = {'entity_id': 'group.{}'.format(group_name)}
    #     data.update(kwargs)
    #     return remote.call_service(self.api, 'homeassistant', 'turn_on', service_data=data)

    # def turn_off_group(self, group_name):
    #     data = {'entity_id': 'group.{}'.format(group_name)}
    #     return remote.call_service(self.api, 'homeassistant', 'turn_off', service_data=data)

    def start_script(self, script_name):
        # data = {'entity_id': 'script.{}'.format(script_name)}
        return remote.call_service(self.api, 'script', 'script_name')

    def command(self, shell_command):
        return remote.call_service(self.api, 'shell_command', shell_command, timeout=10)

