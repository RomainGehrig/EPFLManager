from collections import OrderedDict
from configparser import ConfigParser
import json

import epflmanager.components as components

class InvalidConversion(Exception): pass

def list_converter(s):
    l = json.loads(s)
    if not isinstance(l, list):
        raise InvalidConversion("%s cannot be converted to a list." % l)
    return l

def read_config_file(filename):
    converters = { 'list': list_converter }
    conf = ConfigParser(converters=converters)
    with open(filename, 'r') as f:
        conf.read_file(f)
    return conf

def default_config_file():
    from os.path import join, expanduser
    from functools import reduce
    return reduce(join, [expanduser('~'), '.config','epflmanager','config.ini'])
