import epflmanager.components as components

class Config(components.Component):
    def __init__(self):
        self.configuration = {}
        super(Config, self).__init__("Config")

    def add(self, key, value):
        if key in self.configuration:
            raise Error("Key %s already registered in configuration" % key)
        self.configuration[key] = value

    def get(self, key):
        return self.configuration[key]
