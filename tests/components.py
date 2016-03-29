import epflmanager.components as components

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
