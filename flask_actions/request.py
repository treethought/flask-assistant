# import aniso8601

# class _Request(object):
#     """When an intent is triggered,
#     API.AI sends data to the service in the form of POST request with
#    a body in the format of response to a query.

#    https://docs.api.ai/docs/webhook

#    format -> https://docs.api.ai/docs/query#response
#     """

#     def __init__(self, api_request_payload):

#         self._payload = api_request_payload

#     @property
#     def id(self):
#         return self._payload['id']

#     @property
#     def timestamp(self):
#         return self._payload['timestamp']

#     @property
#     def session_id(self):
#         return self._payload['session_id']

#     @property
#     def status(self):
#         return self._payload['status']

#     @property
#     def intent(self):
#         return _Intent(self._payload['result'])


# class _Field(dict):

#     def __init__(self, request_json={}):
#         super(_Field, self).__init__(request_json)
#         for key, value in request_json.items():
#             if isinstance(value, dict):
#                 value = _Field(value)
#             self[key] = value

#     def __getattr__(self, attr):
#         # converts timestamp str to datetime.datetime object
#         if 'timestamp' in attr:
#             return aniso8601.parse_datetime(self.get(attr))
#         return self.get(attr)

#     def __setattr__(self, key, value):
#         self.__setitem__(key, value)


# class _Intent(object):
#     """Holds the currently matched Intent"""

#     def __init__(self, result_json):
#         self._payload = result_json

#     @property
#     def action(self):
#         return self._payload['action']

#     @property
#     def query(self):
#         return self._payload['resolvedQuery']

#     @property
#     def action_incomplete(self):
#         return self._payload['actionIncomplete']

#     @property
#     def params(self):
#         return self._payload['parameters']

#     @property
#     def contexts(self):
#         contexts = (obj for obj in self._payload['contexts'])
#         yield from contexts

#     @property
#     def name(self):
#         return self._payload['metadata']['intentName']

#     @property
#     def id(self):
#         return self._payload['metadata']['id']
