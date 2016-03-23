""" Components management inspired by the Deluge implementation """

import logging
logger = logging.getLogger(__name__)

class Component(object):
    def __init__(self, name):
        self._component_name = name
        _ComponentRegistry.register(self)

class ComponentRegistry(object):
    def __init__(self, *args, **kwargs):
        self.components = {}

    def register(self, component):
        logger.info("Component %s initialized." % component._component_name)
        name = component._component_name
        if name in self.components:
            raise Error("Component already registered as %s" % name)
        self.components[name] = component

    def get(self, name):
        return self.components.get(name)

    def is_started(self, name):
        return name in self.components

def as_component(obj, name):
    """ Lift an object to be registered as a Component """
    obj._component_name = name
    register(obj)

_ComponentRegistry = ComponentRegistry()

register = _ComponentRegistry.register
get = _ComponentRegistry.get
