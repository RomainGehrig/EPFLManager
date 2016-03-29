import sys
import json
from collections import OrderedDict
from configparser import ConfigParser

import epflmanager.components as components

class InvalidConversion(Exception): pass

def list_converter(s):
    l = json.loads(s)
    if not isinstance(l, list):
        raise InvalidConversion("%s cannot be converted to a list." % l)
    return l

def get_config_parser():
    converters = { 'list': list_converter }
    if sys.version_info < (3, 5):
        def create_new_getter(config, converter):
            def get_and_convert(section, name):
                return converter(config[section][name])
            return get_and_convert

        c = ConfigParser()
        for attr,func in converters.items():
            c.__setattr__("get%s" % attr, create_new_getter(c, func))
        return c
    else:
        return ConfigParser(converters=converters)

def read_config_file(filename):
    conf = get_config_parser()
    with open(filename, 'r') as f:
        conf.read_file(f)
    return conf

def start_config_component(config):
    components.as_component(config, "Config")

def default_config_file():
    from os.path import join, expanduser
    from functools import reduce
    return reduce(join, [expanduser('~'), '.config','epflmanager','config.ini'])
