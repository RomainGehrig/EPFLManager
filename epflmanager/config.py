from collections import OrderedDict
from configparser import ConfigParser

import epflmanager.components as components

class ConfigFileNotFound(FileNotFoundError): pass
class InvalidConversion(Exception): pass

class Config(components.Component):
    def __init__(self):
        self.configuration = OrderedDict()
        super(Config, self).__init__("Config")

    def add(self, key, value):
        if key in self.configuration:
            raise Error("Key %s already registered in configuration" % key)
        self.configuration[key] = value

    def get(self, key):
        return self.configuration[key]

def to_list(s):
    l = json.loads(s)
    if not isinstance(l, list):
        raise InvalidConversion("%s cannot be converted to a list." % l)
    return l

def read_config_files(fs):
    if not isinstance(fs, list):
        fs = [fs,]
    converters = { 'list': to_list }
    conf = ConfigParser(converters=converters)
    conf.read(fs)
    return conf

def possible_config_files():
    from os.path import abspath, expanduser
    return list(map(lambda p: abspath(expanduser(p)), ['~/.config/epflmanager/config.ini','~/.epflmanager']))
