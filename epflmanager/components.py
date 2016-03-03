""" Components management inspired by the Deluge implementation """

class Component(object):
    def __init__(self, name):
        self._component_name = name
        _ComponentRegistry.register(self)

class ComponentRegistry(object):
    def __init__(self, *args, **kwargs):
        self.components = {}

    def register(self, component):
        name = component._component_name
        if name in self.components:
            raise Error("Component already registered as %s" % name)
        self.components[name] = component

    def get(self, name):
        return self.components.get(name)

_ComponentRegistry = ComponentRegistry()

register = _ComponentRegistry.register
get = _ComponentRegistry.get
