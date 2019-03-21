from flask_assistant import logger


def parse_context_name(context_obj):
    """Parses context name from Dialogflow's contextsession prefixed context path"""
    return context_obj["name"].split("/contexts/")[1]


class Context(dict):
    """docstring for _Context"""

    def __init__(self, name, parameters={}, lifespan=5):

        self.name = name
        self.parameters = parameters
        self.lifespan = lifespan
        self._full_name = None

    # def __getattr__(self, param):
    #     if param in ['name', 'parameters', 'lifespan']:
    #         return getattr(self, param)
    #     return self.parameters[param]

    def set(self, param_name, value):
        self.parameters[param_name] = value

    def get(self, param):
        return self.parameters.get(param)

    def sync(self, context_json):
        self.__dict__.update(context_json)

    def __repr__(self):
        return self.name

    @property
    def serialize(self):
        return {
            "name": self._full_name,
            "lifespanCount": self.lifespan,
            "parameters": self.parameters,
        }


class ContextManager:
    def __init__(self, assist):
        self._assist = assist
        self._cache = {}

    @property
    def _project_id(self):
        return self._assist.project_id

    @property
    def _session_id(self):
        return self._assist.session_id

    def build_full_name(self, short_name):
        return "projects/{}/agent/sessions/{}/contexts/{}".format(
            self._project_id, self._session_id, short_name
        )

    def add(self, *args, **kwargs):
        context = Context(*args, **kwargs)
        context._full_name = self.build_full_name(context.name)
        self._cache[context.name] = context
        return context

    def get(self, context_name, default=None):
        return self._cache.get(context_name, default)

    def set(self, context_name, param, val):
        context = self.get(context_name)
        context.set(param, val)
        self._cache[context.name] = context
        return context

    def get_param(self, context_name, param):
        return self._cache[context_name].parameters[param]

    def update(self, contexts_json):
        for obj in contexts_json:
            short_name = parse_context_name(obj)
            context = Context(short_name)
            context._full_name = obj["name"]
            context.lifespan = obj.get("lifespanCount", 0)
            context.parameters = obj.get("parameters", {})
            self._cache[context.name] = context

    def clear_all(self):
        logger.info("Clearing all contexts")
        new_cache = {}
        for name, context in self._cache.items():
            context.lifespan = 0
            new_cache[name] = context

        self._cache = new_cache

    @property
    def status(self):
        return {"Active contexts": self.active, "Expired contexts": self.expired}

    @property
    def active(self):
        return [self._cache[c] for c in self._cache if self._cache[c].lifespan > 0]

    @property
    def expired(self):
        return [self._cache[c] for c in self._cache if self._cache[c].lifespan == 0]
