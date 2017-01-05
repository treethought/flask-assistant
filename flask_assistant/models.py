
from flask import json



class Context(object):
    """docstring for _Context"""
    def __init__(self, name, parameters={}, lifespan=5):

        self.name = name
        self.parameters = parameters
        self.lifespan = lifespan

    def set(self, param_name, value):
        self.parameters[param_name] = value

    def sync(self, context_json):
        self.__dict__.update(context_json)


    @property
    def serialize(self):
        return {"name": self.name, "lifespan": self.lifespan, "parameters": self.parameters}
    

class _Intent(object):
    """Holds the currently matched Intent"""

    def __init__(self, result_json):
        self._payload = result_json
        self.id = self._payload['id']
        self.name = self._payload['name']
        self.context_in = self._payload['contextIn']
        self.context_out = self._payload['contextOut']
        self.actions = self._payload['actions']
        self.parameters = self._payload['parameters']


    @property
    def name(self):
        return self._payload['metadata']['intentName']

    @property
    def action(self):
        return self._payload['action']

    @property
    def query(self):
        return self._payload['resolvedQuery']

    @property
    def action_incomplete(self):
        return self._payload['actionIncomplete']

    @property
    def params(self):
        return self._payload['parameters']

    @property
    def contexts(self):
        contexts = (obj for obj in self._payload['contexts'])
        yield from contexts

    

