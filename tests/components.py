from unittest import mock

from epflmanager.coursehandler import CourseHandler
from epflmanager.config import get_config_parser, start_config_component
import epflmanager.components as components

config_file_content = """
[version]
epflmanager=0.1
configreader=%(epflmanager)s

[directories]
main_dir=/
# the order determines which is the current semester
# (the last member of this list that exists on the disk)
semester_directories=
    ["BA1","BA2","BA3","BA4","BA5","BA6"
    ,"MA1","MA2","MA3","MA4"]
course_urls_file=site.url
moodle_config_file=.moodle.{course_name}
schedule_file=schedule.png

[moodle]
main_url=http://moodle.epfl.ch/
course_url=%(main_url)scourse/view.php?id={course_id}
cookie_file=moodle.cookies
"""

def override_component(component_name, cls, *args, **kwargs):
    # TODO find a way to mock the ComponentRegistry into allowing temporary overriding
    # Maybe something like a context manager?
    ...

def initialize_components():
    setup_config()
    setup_coursehandler()
    setup_console()

def setup_coursehandler():
    if not components.is_started("CourseHandler"):
        CourseHandler()

def setup_console():
    if not components.is_started("Console"):
        NoIOConsole()

def setup_config():
    if not components.is_started("Config"):
        conf = get_config_parser()
        conf.read_string(config_file_content)
        start_config_component(conf)

class NoIOConsole(components.Component):
    """ Doesn't do any IO with the user. Returns default values or dummy ones """
    def __init__(self):
        super().__init__("Console")
        self._default_funcs = {}

    def _save_default_funcs(self, ignores=None):
        if ignores is None:
            ignores = set()

        funcs = {"input","error","warn","info","confirm","password","print","choose_from"}

        for f in funcs.difference(ignores):
            self._default_funcs[f] = self.__getattribute__(f)

    def _restore_default_funcs(self):
        for fname, fbody in self._default_funcs.items():
            self.__setattr__(fname, fbody)

    def __enter__(self):
        self._save_default_funcs()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self._restore_default_funcs()

    def error(self, txt):
        pass
    def warn(self, txt):
        pass
    def info(self, txt):
        pass

    def input(self, text, default=None):
        return default

    def confirm(self, question, default=True):
        return True

    def password(self, text="Password: "):
        return "password"

    def print(self, *args, **kwargs):
        pass

    def choose_from(self, choices, msg=None, display_func=str, can_quit=True, auto_choice_if_unique=True):
        return choices[0]
