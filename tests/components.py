import epflmanager.components as components

class NoIOConsole(components.Component):
    """ Doesn't do any IO with the user. Returns default values or dummy ones """
    def __init__(self):
        super().__init__("Console")

    def patch_func(self, funcname, newfunc):
        """ Dirty hack to change behavior of IO funcs """
        self.__setattr__(funcname, newfunc)

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
